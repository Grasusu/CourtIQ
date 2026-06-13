# Workers

Background jobs should be added after the synchronous MVP works.

Later flow:

1. API receives CSV upload.
2. API creates an `UploadJob`.
3. API stores the uploaded file locally or in S3.
4. Worker validates and processes the CSV.
5. Worker saves metrics and marks the job completed or failed.

Start simple first. A working synchronous upload is better than a half-finished worker system.
