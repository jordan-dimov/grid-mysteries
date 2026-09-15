#!/usr/bin/env bash
# One-time AWS setup for vintage capture (ops/VINTAGE-CAPTURE.md, section 3).
#
#   AWS_PROFILE=<admin profile> ops/aws-bootstrap.sh [bucket] [region]
#
# Creates, idempotently where the API allows:
#   - the log bucket   <bucket>-logs   (private, versioned, log-delivery write)
#   - the vintage bucket <bucket>      (versioned, Object Lock governance mode
#                                       with a 5-year default retention,
#                                       Intelligent-Tiering, server access
#                                       logging to the log bucket, public read
#                                       on manifests/ and proofs/ only)
#   - IAM users and least-privilege policies:
#       vintage-capture-writer   PutObject + GetObject on the vintage bucket
#       vintage-analysis-reader  GetObject + ListBucket on the vintage bucket
#       vintage-watchdog         GetObject + ListBucket on both buckets, plus
#                                GetBucket* settings reads (to check they are unchanged)
#   - one access key per user, printed ONCE at the end (store them; this script
#     never prints them again)
#
# Object Lock must be enabled at bucket creation, which is why the bucket is
# created here and not in the console by hand. Nothing here deletes anything.
set -euo pipefail
BUCKET="${1:-a115-vintages}"
REGION="${2:-eu-west-2}"
LOGS="${BUCKET}-logs"
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
echo "account $ACCOUNT, region $REGION, bucket $BUCKET, logs $LOGS"

bucket_exists() { aws s3api head-bucket --bucket "$1" >/dev/null 2>&1; }

# ---- log bucket -------------------------------------------------------------
if ! bucket_exists "$LOGS"; then
  aws s3api create-bucket --bucket "$LOGS" --region "$REGION" \
    --create-bucket-configuration LocationConstraint="$REGION" >/dev/null
  echo "created $LOGS" >&2
fi
aws s3api put-public-access-block --bucket "$LOGS" --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws s3api put-bucket-versioning --bucket "$LOGS" --versioning-configuration Status=Enabled
aws s3api put-bucket-policy --bucket "$LOGS" --policy "$(cat <<JSON
{"Version":"2012-10-17","Statement":[{"Sid":"S3ServerAccessLogsPolicy","Effect":"Allow",
 "Principal":{"Service":"logging.s3.amazonaws.com"},"Action":"s3:PutObject",
 "Resource":"arn:aws:s3:::$LOGS/access/*",
 "Condition":{"StringEquals":{"aws:SourceAccount":"$ACCOUNT"}}}]}
JSON
)"

# ---- vintage bucket ---------------------------------------------------------
if ! bucket_exists "$BUCKET"; then
  aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" \
    --create-bucket-configuration LocationConstraint="$REGION" \
    --object-lock-enabled-for-bucket >/dev/null
  echo "created $BUCKET (Object Lock enabled)" >&2
fi
aws s3api put-bucket-versioning --bucket "$BUCKET" --versioning-configuration Status=Enabled
aws s3api put-object-lock-configuration --bucket "$BUCKET" --object-lock-configuration \
  '{"ObjectLockEnabled":"Enabled","Rule":{"DefaultRetention":{"Mode":"GOVERNANCE","Years":5}}}'
aws s3api put-bucket-intelligent-tiering-configuration --bucket "$BUCKET" --id all \
  --intelligent-tiering-configuration '{"Id":"all","Status":"Enabled","Tierings":[{"Days":90,"AccessTier":"ARCHIVE_ACCESS"},{"Days":180,"AccessTier":"DEEP_ARCHIVE_ACCESS"}]}'
aws s3api put-bucket-logging --bucket "$BUCKET" --bucket-logging-status \
  "{\"LoggingEnabled\":{\"TargetBucket\":\"$LOGS\",\"TargetPrefix\":\"access/\"}}"
# public read on the two public prefixes only; everything else stays private
aws s3api put-public-access-block --bucket "$BUCKET" --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=false,RestrictPublicBuckets=false
aws s3api put-bucket-policy --bucket "$BUCKET" --policy "$(cat <<JSON
{"Version":"2012-10-17","Statement":[
 {"Sid":"PublicManifestsAndProofs","Effect":"Allow","Principal":"*","Action":"s3:GetObject",
  "Resource":["arn:aws:s3:::$BUCKET/manifests/*","arn:aws:s3:::$BUCKET/proofs/*"]}]}
JSON
)"

# ---- IAM users and policies ---------------------------------------------------
policy() {  # name, document
  local arn="arn:aws:iam::$ACCOUNT:policy/$1"
  if ! aws iam get-policy --policy-arn "$arn" >/dev/null 2>&1; then
    aws iam create-policy --policy-name "$1" --policy-document "$2" >/dev/null
    echo "created policy $1" >&2
  fi
  echo "$arn"
}
user() {  # name, policy arn
  if ! aws iam get-user --user-name "$1" >/dev/null 2>&1; then
    aws iam create-user --user-name "$1" >/dev/null
    echo "created user $1" >&2
  fi
  aws iam attach-user-policy --user-name "$1" --policy-arn "$2"
}
WRITER=$(policy vintage-capture-writer "$(cat <<JSON
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["s3:PutObject","s3:GetObject"],"Resource":"arn:aws:s3:::$BUCKET/*"},
 {"Effect":"Allow","Action":["s3:ListBucket"],"Resource":"arn:aws:s3:::$BUCKET"}]}
JSON
)")
READER=$(policy vintage-analysis-reader "$(cat <<JSON
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["s3:GetObject"],"Resource":"arn:aws:s3:::$BUCKET/*"},
 {"Effect":"Allow","Action":["s3:ListBucket"],"Resource":"arn:aws:s3:::$BUCKET"}]}
JSON
)")
WATCHDOG=$(policy vintage-watchdog "$(cat <<JSON
{"Version":"2012-10-17","Statement":[
 {"Effect":"Allow","Action":["s3:GetObject","s3:ListBucket","s3:GetBucketVersioning",
   "s3:GetBucketObjectLockConfiguration","s3:GetBucketLogging","s3:GetBucketPolicy",
   "s3:GetBucketPublicAccessBlock"],
  "Resource":["arn:aws:s3:::$BUCKET","arn:aws:s3:::$BUCKET/*","arn:aws:s3:::$LOGS","arn:aws:s3:::$LOGS/*"]}]}
JSON
)")
user vintage-capture-writer "$WRITER"
user vintage-analysis-reader "$READER"
user vintage-watchdog "$WATCHDOG"

echo
echo "Access keys (shown once; put the writer's in Render, the watchdog's in ~/.aws/credentials [a115-watchdog]):"
for u in vintage-capture-writer vintage-analysis-reader vintage-watchdog; do
  if [[ "$(aws iam list-access-keys --user-name "$u" --query 'length(AccessKeyMetadata)')" == "0" ]]; then
    aws iam create-access-key --user-name "$u" --query 'AccessKey.[UserName,AccessKeyId,SecretAccessKey]' --output text
  else
    echo "$u already has a key; not creating another"
  fi
done
echo "done. Verify: aws s3api get-object-lock-configuration --bucket $BUCKET"
