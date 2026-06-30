# Storage

Storage adapters isolate where uploaded files are saved.

Current adapter:

- `LocalUploadStorage` writes CSV files to `LOCAL_UPLOAD_DIR` or `local_uploads/`.

Future adapter:

- `S3UploadStorage` can save the same upload bytes to a private S3 bucket and return an S3 object key as `stored_path`.

Routes should depend on the storage adapter contract, not on direct filesystem writes.
