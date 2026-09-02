# Set up some sample data

Use the sample data fixture to populate a local database with data suitable for a demo or development environment.

### Load the sample data

Run:

```bash
django-admin loaddata sample_data
```

This loads the `sample_data.json` fixtures into the current database.

> **Warning:** Loading the fixture may overwrite existing data. Make sure you are using the appropriate database before running this command.
