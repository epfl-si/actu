# ADR-XXX: Migrate the new application from Django 5.2 to Django 6.1

**Status:** Proposed
**Date:** 2026-08-19
**Deciders:** Development Team

## TL;DR

Migrate the new application from **Django 5.2 to Django 6.1**.

The application is a rewrite of an existing Django project whose original use cases are obsolete. The new application is still under development and is not yet in production.

As there is no production deployment to preserve, the Django version of the existing application should not be considered a constraint for the rewrite.

Django 5.2's active support has already ended, while Django 6.1 is the current stable release.

We therefore choose to move the new application to Django 6.1 now rather than continue developing on Django 5.2.

Django 6.2 is expected in April 2027 and will be an LTS release. Its adoption will be evaluated separately when it becomes available.

## Context

The project is a rewrite of an existing Django application.

The existing application was built around use cases that are now obsolete. The purpose of the rewrite is therefore not to reproduce the existing application technically, but to build a new application around the use cases that are currently relevant.

The new application is currently under development and has not yet reached production.

The rewrite currently uses Django 5.2.

Django 5.2 was released in April 2025 as an LTS release. Its active support ended in December 2025, while security and data-loss fixes are scheduled until April 2028.

Django 6.1 was released in August 2026 and is currently the latest stable Django release. Its mainstream support is scheduled until April 2027, followed by security support until December 2027.

The project therefore has an opportunity to update the framework while the application is still being developed, without the constraints normally associated with upgrading an application already in production.

### Django's upcoming release model

Django has announced a significant change to its release model.

Starting in January 2028, Django will move to one feature release per year. Each feature release will receive three years of support: one year of mainstream bug-fix support followed by two years of security and data-loss fixes. The LTS distinction will then be retired.

The transition is expected to be:

| Version        | Release      | Mainstream support | Security support |
| -------------- | ------------ | ------------------ | ---------------- |
| Django 6.1     | August 2026  | April 2027         | December 2027    |
| Django 6.2 LTS | April 2027   | December 2027      | April 2030       |
| Django 2028    | January 2028 | January 2029       | January 2031     |

Django has explicitly stated that the support commitment for Django 6.2 remains unchanged.

This means that Django 6.2 will eventually provide a longer-lived baseline than Django 6.1. However, Django 6.2 is not available at the time of this decision.

## Decision

We will migrate the new application from **Django 5.2 to Django 6.1**.

The migration will be performed while the application is still under development.

The existing application's implementation will not be treated as a compatibility constraint. Where Django 6.1 requires changes to the code, the new application will be adapted directly rather than preserving Django 5.2-specific patterns.

The migration will include:

1. Upgrade Django to the latest available Django 6.1 release.

2. Review the Django 6.0 and 6.1 release notes for backwards-incompatible changes and deprecations.

3. Review and update Django-related third-party dependencies.

4. Verify compatibility of the project's Python dependencies.

5. Verify database compatibility.

6. Adapt the application code where required.

7. Update and extend tests where necessary.

8. Run the complete automated test suite.

9. Continue development using Django 6.1 as the project's framework baseline.

This decision does **not** commit the project to remaining on Django 6.1 until the end of its support period.

Django 6.2 will be evaluated separately when it is released.

## Rationale

The main reason for this decision is the **development status of the application**.

For a production application, upgrading Django can involve significant operational risk, compatibility constraints, and coordination with deployment schedules.

Those constraints do not currently apply here.

The application is still being developed, which means framework compatibility changes can be incorporated directly into the development work. There is also no requirement to preserve obsolete behavior from the existing application.

Continuing to develop on Django 5.2 would effectively mean choosing to build a new application on a framework version whose active support has already ended.

Moving to Django 6.1 now allows the rewrite to use the current Django release and avoids postponing framework modernization until Django 6.2 becomes available.

## Alternatives Considered

### Keep Django 5.2

**Pros:**

- No migration work is required immediately.

- Django 5.2 remains supported for security and data-loss fixes until April 2028.

- The actual tool in production already uses this version.

**Cons:**

- Active support has already ended.

- The new application would continue to be developed against an older Django version.

- The project would inherit a framework version from the previous application without a current technical reason.

- The team would develop obsolete know-how

- A future upgrade would still be required.

**Decision:** Rejected.

The fact that the application is still under development makes this a particularly unattractive option. There is no production compatibility constraint that justifies remaining on Django 5.2.

### Wait for Django 6.2

Django 6.2 is expected in April 2027 and will be an LTS release with support through April 2030.

**Pros:**

- Longer support period.

- Avoids adopting Django 6.1, which has a relatively short remaining support period.

- Provides a stable LTS baseline.

**Cons:**

- Django 6.2 is not currently available.

- Development would continue on Django 5.2 in the meantime.

- The project would delay adoption of the current Django release.

- There is no production constraint requiring us to wait for an LTS release.

**Decision:** Rejected for now.

We prefer to migrate the application to Django 6.1 now. Django 6.2 will be evaluated when it becomes available.

## Consequences

### Positive

- The rewrite uses the current Django release.

- The project no longer develops against a Django version whose active support has ended.

- Django 6.1 compatibility issues can be addressed while the application is still under development.

- The project gains experience with Django 6.x before the next framework upgrade.

### Negative

- The migration requires development effort now.

- Some application code may need to be changed.

- Some third-party dependencies may need to be upgraded or replaced.

- Django 6.1 has a relatively short support period compared with Django 5.2 LTS.

- Another Django upgrade, potentially to Django 6.2, may be appropriate after its release.

## Future Upgrade Strategy

The project should therefore aim for the 6.2 LTS rather than allowing large version gaps to accumulate.

A possible and wanted future path is:

**Django 6.1 → Django 6.2 LTS**

## Risks and Mitigations

**Risk:** A third-party dependency is not compatible with Django 6.1.

**Mitigation:** Review Django-related dependencies before the upgrade and update or replace incompatible packages.

**Risk:** Django 6.1 requires changes to application code.

**Mitigation:** Address compatibility changes as part of normal development and update the automated test suite accordingly.

**Risk:** The project remains on Django 6.1 longer than intended because the application has not yet reached production.

**Mitigation:** Track Django's release lifecycle and explicitly evaluate Django 6.2 when it becomes available.

**Risk:** The rewrite reproduces technical decisions from the obsolete application unnecessarily.

**Mitigation:** Treat the existing application primarily as a source of functional requirements. Technical decisions should be reconsidered for the new application.

## References

- [Django — Moving to an annual release cycle](https://www.djangoproject.com/weblog/2026/aug/10/annual-release-cycle/) — official announcement of Django's new release and support model.

- [Django lifecycle — endoflife.date](https://endoflife.date/django) — Django release and support lifecycle.

- [Django 6.1 release notes](https://docs.djangoproject.com/en/6.1/releases/6.1/)

- [Django supported versions](https://www.djangoproject.com/download/)

- [Django upgrade guide](https://docs.djangoproject.com/en/6.1/howto/upgrade-version/)


