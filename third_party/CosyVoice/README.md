This directory contains a lightweight local CosyVoice fixture for workspace
verification.

It provides the `cosyvoice.cli.cosyvoice.AutoModel` import expected by the
runtime so the live browser tests can exercise the real `/generate` and
`/generations/{job_id}` endpoints without depending on an external model
checkout in this workspace.
