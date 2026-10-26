# Changelog

## v0.0.7 / 2026-10-14

- Implement OPDo audit log (#133)
- Fix bash code incompatible with Macos (#136)
- Preview and View a news + redirect to other translation on lang switch (#122)
- Add link to the search page in the mobile menu (#129)
- [feat] Display Commons licence of a news if checked (#128)
- [fix] Run build-assets before coverage (#126)
- Add initial AGENTS.md (#125)
- Add React Islands (#120)
- Add API News images endpoint + fix nginx/media config (#121)
- Add some slugs and urls to news seeds for the db (#124)
- Add a way to run playwright tests locally (#123)
- Fix pushing integers into the stringData structure (#117)
- Fix the deprecated usage of local_action (#118)
- Fix accessing fact as vars (#119)
- Add missing namespaces definition (#116)
- Add a way to skip the suitcase installation, giving some room for other ways
- [feature] Add make command to seed db with sample_data (#114)
- Rename "thematic" to "topic"
- Add title on the search page and fine-tune spacing (#109)
- [feature] Add urls (#104)
- Create NewsImage model (#112)
- Fix having debug-toolbar started when running local tests
- Feature/edit create news status (#105)
- Activate Django media uploads (settings, folder) (#111)
- Set the link to the search page in the header (#108)
- Fix having two times the LanguageConverter registered

## v0.0.6 / 2026-09-22

- Feature/filter news (#96)
- [fix] Fix TinyMCE warning: add licence_key gpl (#97)
- Fix sample data for news (#103)
- Increase save button size on Edit news page (#102)
- Reduce filter buttons size (#101)
- Fix errors highlighting and display on Edit news page (#100)
- Remove news title in Edit news page h1 (#99)
- Optionally display news metadata in the Manage news page (#98)
- Add samples data for news (#95)
- Set at the Model level that it is not allowed for a news to live without a thematic or a format (#94)
- Add news API endpoint (#88)
- Add auto-slug to NewsTranslation with slug history table (#87)
- Add maxlength and required properties on title of edit news page (#92)
- Remove current_label templatetags (#93)
- Feature/list news (#86)
- Standardize format label (#91)
- Add search and filters to Manage News (#90)
- Additional TinyMCE fields for news (#76)
- Update some sample_data to reflect what will be prod values for thematic and entities (#89)
- Create and edit news (#68)
- Fix Audit Log N+1 queries (#84)
- Explain how to access the API doc (#85)
- Add entities API endpoint (#79)
- Add pagination on Manage News page (#83)
- Add some sample data to have a starting dev site
- Add thematics API endpoint (#77)
- Improve Playwright test case setup and teardown (#82)
- Ensure modal close aria-label is translatable (#81)
- Avoid creating AccredServiceClient twice (#80)
- Add homemade log audit (#75)
- Add Manage News page (#72)
- Configure Django REST Framework and drf-spectacular (#73)
- Add some doc about debugging on Intellij
- Update django-epfl-web2018 to 0.0.8 (#69)
- Fix using too fresh NPM libraries
- Add news_formats and block_types models (#56)
- Add a diataxis doc structure and some guidance on how to start developing
- Git ignore the collectstatic target folder when using django collectstatic
- Update django to 5.2.17 (#65)
- Configure Oxc minifier to strip console/debugger in production (#66)

## v0.0.5 / 2026-08-07

- Add homepage permission page (#51)
- Add Manage homepages page (#50)
- Add eslint (#63)
- Add sass pipeline (#54)
- feature: links to homepages and news in user menu (POC) (#61)
- Configure hot module replacement (HMR) with django-vite (#58)

## v0.0.4 / 2026-07-24

- Update django-debug-toolbar to 7.0.0 (#57)
- Fix order of LocaleMiddleware (#59)
- Improve CONTRIBUTING.md (#55)
- Add .dockerignore (#53)
- Update codecov/codecov-action to v7 (#52)
- Integrate EPFL API communication (#44)
- Feature/entities footer (#60)
- Add ViteJS to Django (#49)

## v0.0.3 / 2026-07-02

- Add Homepage model (#40)
- Add HomepageTranslation model (#45)
- Add News and NewsTranslation models (#41)
- Add entity and thematic order management (#37)
- Add email configuration (#36)
- Show thematics in header (#38)
- Implement strict access control based on Entra ID authorization (#47)
- Improve User admin and display (#42)
- Fix admin login redirect with language prefix (#43)
- Show deprecated APIs/symbols as warnings in VS Code (#46)

## v0.0.2 / 2026-06-02

- Add models entities and thematics (#30)
- Add Web2018 templates (#33)
- Add clone DB (#34)
- Add german and italian languages (#32)

## v0.0.1 / 2026-05-22

- [feature] add config as code for deploying on OpenShift with Ansible (#28)
- Set Time Zone (#29)
- Add and configure languages (#24)
- Implement Entra ID authentication (#27)
- Add Web2018 error pages (#26)
- Create custom User model with EPFL SCIPER field (#25)
- Add Django Debug Toolbar (#21)
- Add pipdeptree (#23)
- Add Debug config for Zed editor (#22)
- Add Trivy - Security scanner (#19)
- Enable hashing for static files (#20)
- Add Playwright test runner (#16)
- Add Hadolint - Dockerfile Linter (#18)
- Build and deploy to ghcr (#17)
- Add code coverage (#14)
- Configure Actu for debugging inside Docker (#13)
- Add Docker environment for production (#15)
- Add CI with GitHub Actions (#11)
- Add liveness probe (#12)
- Add Docker environment for development (#10)
- Add VS Code settings (#8)
- Init Django project (#9)
- Add optional Python venv for development (#7)
- Add VS Code recommended extensions (#6)
- Add isort (#5)
- Add Black (#3)
- Init Makefile (#4)
- Add Flake8 (#2)
- Add EditorConfig (#1)
- [doc] Update README
- [doc] Add CHANGELOG
- [doc] Add CONTRIBUTING.md
- Initial commit
