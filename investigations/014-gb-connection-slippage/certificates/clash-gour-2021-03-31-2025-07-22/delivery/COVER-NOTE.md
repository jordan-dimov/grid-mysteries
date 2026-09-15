# Cover note — As-of Connection Record Certificate, Clash Gour

Attached is the certificate (PDF) and the evidence bundle it rests on, as a
directory. The certificate states what NESO's published TEC Register said
about Clash Gour on 31 March 2021 and on 22 July 2025, and every change
between those dates with the copy of the register that first showed it. It
is a factual record of publication only: it contains no forecast, no view on
why any value changed, and no opinion on entitlement.

To verify the bundle without contacting us or any network: open the bundle
directory and run `python3 verify.py` (Python 3, standard library only). It
recomputes the SHA-256 of every file listed in `MANIFEST.json`, confirms that
the manifest's own digest is the certificate id printed on the PDF, and
checks that the two full register copies in `registers/` hash to the digests
the acquisition journal recorded for them. The files
`MANIFEST.json.freetsa.tsr` and `MANIFEST.json.digicert.tsr` are RFC 3161
timestamp tokens binding that digest to the clocks of freetsa.org and
DigiCert; `openssl ts -verify -in MANIFEST.json.freetsa.tsr -queryfile
MANIFEST.json.tsq -CAfile <freetsa root certificate>` checks one (the root
certificates are in the repository under `trust/tsa/`, and the same commands
apply to `CERTIFICATE.md`). `MANIFEST.json.ots` is an OpenTimestamps proof
anchoring the same digest in the Bitcoin blockchain, checkable with the
`ots` client. The method, code and tests are public in the repository named
on the certificate, so the record can be regenerated from the archived
register copies and compared.
