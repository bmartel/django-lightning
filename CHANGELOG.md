# CHANGELOG


## v0.9.8 (2026-07-28)

### Bug Fixes

- **k8s**: Exclude dev-deployment.yaml via ignorePaths and update .kube-linter.yaml exclusions
  ([`c784866`](https://github.com/bmartel/django-lightning/commit/c784866a3fd5c3dc09f7a16f073bf67ea13bb839))

- **k8s**: Harden securityContext with readOnlyRootFilesystem and addAllBuiltIn in kube-linter
  config
  ([`83d0e3b`](https://github.com/bmartel/django-lightning/commit/83d0e3bf838a815259023e9a796a205dd5451d11))


## v0.9.7 (2026-07-28)

### Bug Fixes

- **k8s**: Update .kube-linter.yaml exclusions and add podAntiAffinity to production deployments
  ([`a7dfbf2`](https://github.com/bmartel/django-lightning/commit/a7dfbf2e4ed66b7ddbc57efca7bb3d9591505c49))


## v0.9.6 (2026-07-28)

### Bug Fixes

- **k8s**: Add .kube-linter.yaml config and securityContext to k8s manifests to pass kube-linter
  validation
  ([`64960c3`](https://github.com/bmartel/django-lightning/commit/64960c3f03138c079744f31bf62594927cdfc78d))

### Documentation

- Update README with Native Rust Core interop, type safety, and memory transfer architecture
  ([`e7c09e9`](https://github.com/bmartel/django-lightning/commit/e7c09e92e11edd390f6fde66307a87f20c085e1f))


## v0.9.5 (2026-07-28)

### Bug Fixes

- **docker**: Export RUSTUP_HOME and CARGO_HOME in Dockerfile for rustup toolchain resolution
  ([`76f79f5`](https://github.com/bmartel/django-lightning/commit/76f79f5af7532b375c7c135481ffafcc1119b15a))


## v0.9.4 (2026-07-28)

### Bug Fixes

- **docker**: Use official rust:1-slim toolchain image in Dockerfile builder to support Cargo
  lockfile v4
  ([`e871934`](https://github.com/bmartel/django-lightning/commit/e871934c499bdc704298dc4051886a516bdbcc13))


## v0.9.3 (2026-07-28)

### Bug Fixes

- **ci**: Compile native extension in CI setup step and add safe import guard in test_native.py
  ([`e74332d`](https://github.com/bmartel/django-lightning/commit/e74332d77f9e0bc3d904d13fdb37800b925bf6e8))


## v0.9.2 (2026-07-28)

### Bug Fixes

- **build**: Set build-backend to setuptools.build_meta in pyproject.toml to decouple project
  packaging from maturin crate compilation
  ([`7d2c4e9`](https://github.com/bmartel/django-lightning/commit/7d2c4e90f77a9476e875201f5e8c3ad57b77b6b5))


## v0.9.1 (2026-07-28)

### Bug Fixes

- **docker**: Use maturin build in release wheel pipeline to fix docker image build step
  ([`fc3cff0`](https://github.com/bmartel/django-lightning/commit/fc3cff0bbd64389c280b6f7a0f99f75d2fe804fb))


## v0.9.0 (2026-07-28)

### Features

- **native**: Make Rust integration explicit and optimize Docker Compose dev DX
  ([`de6e99d`](https://github.com/bmartel/django-lightning/commit/de6e99da512309682c58aaef6ca9bc032b5459b6))


## v0.8.0 (2026-07-28)

### Features

- **native**: Improve developer ergonomics with native_json decorator factory
  ([`ebec695`](https://github.com/bmartel/django-lightning/commit/ebec6950aeba65700e0b6181dd06c22a968a5c46))


## v0.7.0 (2026-07-28)

### Documentation

- **skills**: Update django-bolt-rust-interop skill guidance with comprehensive PyO3 best practices
  ([`73db4d6`](https://github.com/bmartel/django-lightning/commit/73db4d6ee1424ab238d7112123b6db7b622a2d38))

### Features

- **native**: Add type-safe @native_async decorator and ultra-fast msgspec JSON bytes FFI helper
  ([`107ff13`](https://github.com/bmartel/django-lightning/commit/107ff1307529eaf82e1874f9567dc0806507ad01))

### Refactoring

- **native**: Replace dummy demo functions with clean interop helpers
  ([`b7f5fdb`](https://github.com/bmartel/django-lightning/commit/b7f5fdb13da8574b8d396f26ad69b40159a87937))


## v0.6.0 (2026-07-28)

### Features

- **rust**: Add native Rust interop, optional scaffolding, and agent skill guidance
  ([`1977696`](https://github.com/bmartel/django-lightning/commit/19776964942290a8721ab36974d5f0ec89218ec4))


## v0.5.0 (2026-07-26)


## v0.4.1 (2026-07-26)

### Bug Fixes

- **profiling**: Add user_date_joined_idx index and enhance SQLite/Postgres EXPLAIN parser
  ([`f741086`](https://github.com/bmartel/django-lightning/commit/f74108644e8bdc2b8752e840215d803641efc6b7))

### Features

- Add comprehensive agent skill documentation, project creation script, and CLI stub to
  django-lightning
  ([`ad3b0c9`](https://github.com/bmartel/django-lightning/commit/ad3b0c9d72dd520e8816434a022fcab40e9d35ef))


## v0.4.0 (2026-07-26)

### Features

- **profiling**: Add surgical query scalability profiler, latency budget guard, and query
  performance rules
  ([`a034363`](https://github.com/bmartel/django-lightning/commit/a0343632a867180ba92cae7ecbe853c106fcf563))


## v0.3.5 (2026-07-26)

### Bug Fixes

- **ci**: Pass --allow-dirty to cargo publish to allow updated lockfile in release workflow
  ([`2e3f9b5`](https://github.com/bmartel/django-lightning/commit/2e3f9b5cd5beefaab8aef771567ec389f00a8a79))


## v0.3.4 (2026-07-26)

### Bug Fixes

- **ci**: Move continue-on-error to step level for crates.io publishing
  ([`7618390`](https://github.com/bmartel/django-lightning/commit/7618390e98672e3c0d977c297ce19ae5fe2bb24b))


## v0.3.3 (2026-07-26)

### Bug Fixes

- **cli**: Fix println macro format string syntax error in scaffolding completion message
  ([`edd4d50`](https://github.com/bmartel/django-lightning/commit/edd4d5010cda31dfb904b012fd44ca630f85bc13))


## v0.3.2 (2026-07-26)

### Bug Fixes

- **ci**: Fix dependabot workflow syntax and cargo build packaging paths in release workflow
  ([`9e5ba3a`](https://github.com/bmartel/django-lightning/commit/9e5ba3aa2514a775565ffcd5663f3df422ed6d91))


## v0.3.1 (2026-07-26)

### Bug Fixes

- **ci**: Fix invalid action versions and track Cargo.toml version in semantic release
  ([`f6c7195`](https://github.com/bmartel/django-lightning/commit/f6c7195449140586bbc300dba7c2772984258662))


## v0.3.0 (2026-07-26)

### Bug Fixes

- **ci**: Add --validate=false to kubectl dry-run in deploy-k8s workflow
  ([`df84516`](https://github.com/bmartel/django-lightning/commit/df845165881467f453a60b61b8625841969642c2))

- **ci**: Enable semantic release workflow for bmartel/django-lightning repository
  ([`3430b7d`](https://github.com/bmartel/django-lightning/commit/3430b7da767e9717373af76a34d7781806fe6973))

- **ci**: Fix build_command type in pyproject.toml for semantic release v9
  ([`f04e5b6`](https://github.com/bmartel/django-lightning/commit/f04e5b655fed90f7f600a8b960e53d379b013015))

- **ci**: Use offline YAML validation & kube-linter in deploy-k8s workflow
  ([`a8cf18c`](https://github.com/bmartel/django-lightning/commit/a8cf18cc0ef30ea8be933356cb2bf1c68bc46d76))

- **cli**: Add collectstatic step to scaffolding next steps instructions
  ([`6562535`](https://github.com/bmartel/django-lightning/commit/6562535a082b153b853757de3d2474ad2987abc6))

- **docker**: Remove README.md from .dockerignore for build context availability
  ([`d87b2d4`](https://github.com/bmartel/django-lightning/commit/d87b2d454c01e2c96f5e55c6b8a48579f0d1b17b))

- **starter**: Move BoltAPI instance to app/api.py for runbolt autodiscovery
  ([`91caf3d`](https://github.com/bmartel/django-lightning/commit/91caf3d487e9e78cc6dc28fd18256975a28b3416))

### Chores

- **deps**: Bump azure/setup-kubectl from 4 to 5
  ([#13](https://github.com/bmartel/django-lightning/pull/13),
  [`b38a5a0`](https://github.com/bmartel/django-lightning/commit/b38a5a0d9029af2c7d54fa76b694324d2cf254c8))

Bumps [azure/setup-kubectl](https://github.com/azure/setup-kubectl) from 4 to 5. - [Release
  notes](https://github.com/azure/setup-kubectl/releases) -
  [Changelog](https://github.com/Azure/setup-kubectl/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/azure/setup-kubectl/compare/v4...v5)

--- updated-dependencies: - dependency-name: azure/setup-kubectl dependency-version: '5'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Continuous Integration

- Auto-approve dependabot PRs and grant workflow permissions
  ([`d1dfe4d`](https://github.com/bmartel/django-lightning/commit/d1dfe4d15fdc29f4ceaee7c710e267d486f5293f))

- Remove approval step from dependabot automerge
  ([`47912eb`](https://github.com/bmartel/django-lightning/commit/47912eb6e19e166176d095101776c61aee14f025))

- Use ADMIN_PAT secret in dependabot auto-merge workflow
  ([`99e7a08`](https://github.com/bmartel/django-lightning/commit/99e7a08fddb90ea08bbcf2898fc3af65b18306cd))

- **release**: Use ADMIN_PAT secret to bypass branch protection in semantic release workflow
  ([`f2d3c67`](https://github.com/bmartel/django-lightning/commit/f2d3c6724cbf00b250421019a2e74ebcaaea94fd))

### Features

- Add built-in async migration management & zero-downtime deployment capabilities
  ([`a839761`](https://github.com/bmartel/django-lightning/commit/a8397613fa220bd24594ba5eef25647ec64a2972))

- **infra**: Optimize production Dockerfile, add user validation, and add dev/prod Compose and K8s
  manifests
  ([`c7ca832`](https://github.com/bmartel/django-lightning/commit/c7ca832a4871627846bbbde886ab8bfa61eafd27))

- **installer**: Add Windows PowerShell standalone 1-line installer script
  ([`432edfc`](https://github.com/bmartel/django-lightning/commit/432edfccfdf8a571b74af2ff678beabd01059033))

- **utils**: Add akeyset_chunker for high-throughput batching and PgBouncer safety
  ([`4c58ae6`](https://github.com/bmartel/django-lightning/commit/4c58ae64618807805aa400cf49c7cfac9e863b5e))


## v0.2.3 (2026-07-25)

### Bug Fixes

- Dependabot automerge without self-review approval requirement
  ([`214b5cf`](https://github.com/bmartel/django-lightning/commit/214b5cf0d8f666ce0ece6321bbdf234102e704c9))

### Chores

- **deps**: Bump actions/checkout from 4 to 7
  ([#1](https://github.com/bmartel/django-lightning/pull/1),
  [`1865005`](https://github.com/bmartel/django-lightning/commit/186500537eba7cb106ac9c8524f629d7cc2f74b5))

Bumps [actions/checkout](https://github.com/actions/checkout) from 4 to 7. - [Release
  notes](https://github.com/actions/checkout/releases) -
  [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/actions/checkout/compare/v4...v7)

--- updated-dependencies: - dependency-name: actions/checkout dependency-version: '7'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump astral-sh/setup-uv from 3 to 7
  ([#4](https://github.com/bmartel/django-lightning/pull/4),
  [`a01ad06`](https://github.com/bmartel/django-lightning/commit/a01ad06bc621060257e8f4bf0ddbb9082112a9ff))

Bumps [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) from 3 to 7. - [Release
  notes](https://github.com/astral-sh/setup-uv/releases) -
  [Commits](https://github.com/astral-sh/setup-uv/compare/v3...v7)

--- updated-dependencies: - dependency-name: astral-sh/setup-uv dependency-version: '7'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump colored from 2.2.0 to 3.1.1 in /cli
  ([#5](https://github.com/bmartel/django-lightning/pull/5),
  [`6ec9a60`](https://github.com/bmartel/django-lightning/commit/6ec9a605038a83a2cf758423bfb704b123e6c2d1))

Bumps [colored](https://github.com/mackwic/colored) from 2.2.0 to 3.1.1. - [Release
  notes](https://github.com/mackwic/colored/releases) -
  [Changelog](https://github.com/colored-rs/colored/blob/master/CHANGELOG.md) -
  [Commits](https://github.com/mackwic/colored/compare/v2.2.0...v3.1.1)

--- updated-dependencies: - dependency-name: colored dependency-version: 3.1.1

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump dialoguer from 0.11.0 to 0.12.0 in /cli
  ([#6](https://github.com/bmartel/django-lightning/pull/6),
  [`0ae26ef`](https://github.com/bmartel/django-lightning/commit/0ae26efe160136b3165a52caf62b1cb39897ce0c))

Bumps [dialoguer](https://github.com/console-rs/dialoguer) from 0.11.0 to 0.12.0. - [Release
  notes](https://github.com/console-rs/dialoguer/releases) -
  [Changelog](https://github.com/console-rs/dialoguer/blob/main/CHANGELOG-OLD.md) -
  [Commits](https://github.com/console-rs/dialoguer/compare/v0.11.0...v0.12.0)

--- updated-dependencies: - dependency-name: dialoguer dependency-version: 0.12.0

dependency-type: direct:production

update-type: version-update:semver-minor ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Update dj-database-url requirement from >=2.2.0 to >=3.1.2
  ([#9](https://github.com/bmartel/django-lightning/pull/9),
  [`61d32c9`](https://github.com/bmartel/django-lightning/commit/61d32c9641cd102f79a910d5520d99dcabc8a1d9))

Updates the requirements on [dj-database-url](https://github.com/jazzband/dj-database-url) to permit
  the latest version. - [Release notes](https://github.com/jazzband/dj-database-url/releases) -
  [Changelog](https://github.com/jazzband/dj-database-url/blob/master/CHANGELOG.md) -
  [Commits](https://github.com/jazzband/dj-database-url/compare/v2.2.0...v3.1.2)

--- updated-dependencies: - dependency-name: dj-database-url dependency-version: 3.1.2

dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Update pytest-asyncio requirement
  ([#11](https://github.com/bmartel/django-lightning/pull/11),
  [`30e91ed`](https://github.com/bmartel/django-lightning/commit/30e91ed1fe51fa1e69dbc0dbfb8814aca00ef100))

Updates the requirements on [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) to permit
  the latest version. - [Release notes](https://github.com/pytest-dev/pytest-asyncio/releases) -
  [Commits](https://github.com/pytest-dev/pytest-asyncio/compare/v0.23.0...v1.4.0)

--- updated-dependencies: - dependency-name: pytest-asyncio dependency-version: 1.4.0

dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Update pytest-django requirement
  ([#10](https://github.com/bmartel/django-lightning/pull/10),
  [`7479eb7`](https://github.com/bmartel/django-lightning/commit/7479eb760ff22b9790c85d26bf51390444c68c5d))

Updates the requirements on [pytest-django](https://github.com/pytest-dev/pytest-django) to permit
  the latest version. - [Release notes](https://github.com/pytest-dev/pytest-django/releases) -
  [Changelog](https://github.com/pytest-dev/pytest-django/blob/main/docs/changelog.rst) -
  [Commits](https://github.com/pytest-dev/pytest-django/compare/v4.8.0...v4.12.0)

--- updated-dependencies: - dependency-name: pytest-django dependency-version: 4.12.0

dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Features

- Add automated semantic release workflow for applications and exclude CLI artifacts from
  scaffolding
  ([`c747708`](https://github.com/bmartel/django-lightning/commit/c74770873aa02fb1fc9beacd67915ebfcac1783e))


## v0.2.1 (2026-07-25)

### Bug Fixes

- 2-stage atomic release pipeline and dependabot pull_request_target permissions
  ([`e374375`](https://github.com/bmartel/django-lightning/commit/e374375c1cb480100aa74c3db2827d884e7e5d2a))


## v0.2.0 (2026-07-25)

### Documentation

- Finalize comprehensive agent skills index and directory tree documentation
  ([`4b2c08e`](https://github.com/bmartel/django-lightning/commit/4b2c08ec633fba064e6792e502e1b07ca58df0ca))


## v0.1.9 (2026-07-25)

### Features

- Ultra-high-throughput async SAQ background worker queue integration
  ([`a3534bd`](https://github.com/bmartel/django-lightning/commit/a3534bdc38a1a629306cc3d2be29a9d836dcc3cb))


## v0.1.8 (2026-07-25)

### Features

- Add dependabot configuration and dependabot auto-merge workflow
  ([`d312b9f`](https://github.com/bmartel/django-lightning/commit/d312b9fb53d4ab92a2567cfa704fef18e21aef7c))


## v0.1.7 (2026-07-25)

### Bug Fixes

- Change fly deployment workflow trigger to manual dispatch and bump crate version to 0.1.7
  ([`d0c7ff3`](https://github.com/bmartel/django-lightning/commit/d0c7ff3cc6c2962dcd2f4e42e878f86def9852b0))


## v0.1.6 (2026-07-25)

### Features

- Preconfigured github workflows for CI/CD, fly.io, and kubernetes
  ([`e2c86bd`](https://github.com/bmartel/django-lightning/commit/e2c86bd637ba5ccda1336772936bd172376d6302))


## v0.1.5 (2026-07-25)

### Bug Fixes

- Robust directory check for existing empty and non-empty destination paths
  ([`56b4374`](https://github.com/bmartel/django-lightning/commit/56b437424e246c8e925e5e6c40210b1a7728122f))


## v0.1.4 (2026-07-25)

### Bug Fixes

- Template resolution when running create-django-bolt outside template workspace
  ([`4409d3b`](https://github.com/bmartel/django-lightning/commit/4409d3b01cc25944f99319504d445bb40e818add))


## v0.1.3 (2026-07-25)

### Bug Fixes

- Install to user local bin directory without requiring sudo
  ([`74cabd3`](https://github.com/bmartel/django-lightning/commit/74cabd3d1920ed864bf712528a27524fe7c28836))

- Use macos-latest runner with target cross-compilation
  ([`8c5679e`](https://github.com/bmartel/django-lightning/commit/8c5679ea94199aa56aa4126d905e731c2df79b7c))


## v0.1.2 (2026-07-25)

### Bug Fixes

- Simplified build runner matrix for cross-platform release binaries
  ([`6f81095`](https://github.com/bmartel/django-lightning/commit/6f810954bff2b80dc0a09ce6a136b21f91048a5c))


## v0.1.1 (2026-07-25)

### Bug Fixes

- Grant write permissions for github release workflow
  ([`aba27b5`](https://github.com/bmartel/django-lightning/commit/aba27b5a49f173ba6d99905e37151753af59510f))


## v0.1.0 (2026-07-25)

### Chores

- Ignore rust build target directory
  ([`b3461ee`](https://github.com/bmartel/django-lightning/commit/b3461eea362a96f81e74581c2078ae65393c5511))

### Features

- Initial commit for django-lightning agentic starter project
  ([`f50bfd1`](https://github.com/bmartel/django-lightning/commit/f50bfd15cc3c10652a1a268dfb6daf0e2bbf8c1a))
