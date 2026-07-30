# CHANGELOG


## v0.18.2 (2026-07-30)

### Bug Fixes

- **security**: Resolve CodeQL alerts for API key hashing and workflow permissions
  ([`3dbe318`](https://github.com/bmartel/django-lightning/commit/3dbe31849a4f625b2c0cba29628484259fd5f1c3))

### Chores

- **deps**: Bump actions/checkout from 4 to 7
  ([#16](https://github.com/bmartel/django-lightning/pull/16),
  [`d7c1727`](https://github.com/bmartel/django-lightning/commit/d7c1727a03350225096fcb13447589f3aa710aa0))

Bumps [actions/checkout](https://github.com/actions/checkout) from 4 to 7. - [Release
  notes](https://github.com/actions/checkout/releases) -
  [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/actions/checkout/compare/v4...v7)

--- updated-dependencies: - dependency-name: actions/checkout dependency-version: '7'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump actions/download-artifact from 4 to 8
  ([#17](https://github.com/bmartel/django-lightning/pull/17),
  [`c682aa2`](https://github.com/bmartel/django-lightning/commit/c682aa2e3a89e3834d1dc95e64d623343275f36e))

Bumps [actions/download-artifact](https://github.com/actions/download-artifact) from 4 to 8. -
  [Release notes](https://github.com/actions/download-artifact/releases) -
  [Commits](https://github.com/actions/download-artifact/compare/v4...v8)

--- updated-dependencies: - dependency-name: actions/download-artifact dependency-version: '8'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump astral-sh/setup-uv from 5 to 7
  ([#15](https://github.com/bmartel/django-lightning/pull/15),
  [`6c51d08`](https://github.com/bmartel/django-lightning/commit/6c51d08efde1d5775579b8338e23c6388b8ae925))

Bumps [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) from 5 to 7. - [Release
  notes](https://github.com/astral-sh/setup-uv/releases) -
  [Commits](https://github.com/astral-sh/setup-uv/compare/v5...v7)

--- updated-dependencies: - dependency-name: astral-sh/setup-uv dependency-version: '7'

dependency-type: direct:production

update-type: version-update:semver-major ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump the cargo group across 1 directory with 1 update
  ([#14](https://github.com/bmartel/django-lightning/pull/14),
  [`898c7ab`](https://github.com/bmartel/django-lightning/commit/898c7abc4b08826530415901548000acc58003b4))

* chore(deps): bump the cargo group across 1 directory with 1 update

Bumps the cargo group with 1 update in the /rust_core directory:
  [pyo3](https://github.com/pyo3/pyo3).

Updates `pyo3` from 0.22.6 to 0.29.0 - [Release notes](https://github.com/pyo3/pyo3/releases) -
  [Changelog](https://github.com/PyO3/pyo3/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/pyo3/pyo3/compare/v0.22.6...v0.29.0)

--- updated-dependencies: - dependency-name: pyo3 dependency-version: 0.29.0

dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

* fix(rust_core): adapt PyO3 0.29 API changes and update dependabot automerge workflow

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: bmartel <brandonmartel@gmail.com>

- **deps**: Update django-bolt requirement from >=0.7.0 to >=0.9.1
  ([#22](https://github.com/bmartel/django-lightning/pull/22),
  [`a9e86c5`](https://github.com/bmartel/django-lightning/commit/a9e86c5140efd69a8fd0ea697b072a2e0377faa2))

Updates the requirements on [django-bolt](https://github.com/dj-bolt/django-bolt) to permit the
  latest version. - [Release notes](https://github.com/dj-bolt/django-bolt/releases) -
  [Changelog](https://github.com/dj-bolt/django-bolt/blob/master/CHANGELOG.md) -
  [Commits](https://github.com/dj-bolt/django-bolt/compare/v0.7.0...v0.9.1)

--- updated-dependencies: - dependency-name: django-bolt dependency-version: 0.9.1

dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Update django-cors-headers requirement
  ([#29](https://github.com/bmartel/django-lightning/pull/29),
  [`e830475`](https://github.com/bmartel/django-lightning/commit/e830475438e8e8968ffe3e3064c160a4899c58af))

Updates the requirements on [django-cors-headers](https://github.com/adamchainz/django-cors-headers)
  to permit the latest version. -
  [Changelog](https://github.com/adamchainz/django-cors-headers/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/adamchainz/django-cors-headers/compare/4.4.0...4.9.0)

--- updated-dependencies: - dependency-name: django-cors-headers dependency-version: 4.9.0

dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Update msgspec requirement from >=0.18.0 to >=0.21.1
  ([#23](https://github.com/bmartel/django-lightning/pull/23),
  [`994aa00`](https://github.com/bmartel/django-lightning/commit/994aa0072253c429fe672553eeadbb1b9c035f41))

Updates the requirements on [msgspec](https://github.com/jcrist/msgspec) to permit the latest
  version. - [Release notes](https://github.com/jcrist/msgspec/releases) -
  [Changelog](https://github.com/msgspec/msgspec/blob/main/docs/changelog.md) -
  [Commits](https://github.com/jcrist/msgspec/compare/0.18.0...0.21.1)

--- updated-dependencies: - dependency-name: msgspec dependency-version: 0.21.1

dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Update pyjwt requirement from >=2.8.0 to >=2.13.0
  ([#31](https://github.com/bmartel/django-lightning/pull/31),
  [`5d1123e`](https://github.com/bmartel/django-lightning/commit/5d1123eeb2e4120d4820029865c34390df3340d2))

Updates the requirements on [pyjwt](https://github.com/jpadilla/pyjwt) to permit the latest version.
  - [Release notes](https://github.com/jpadilla/pyjwt/releases) -
  [Changelog](https://github.com/jpadilla/pyjwt/blob/master/CHANGELOG.rst) -
  [Commits](https://github.com/jpadilla/pyjwt/compare/2.8.0...2.13.0)

--- updated-dependencies: - dependency-name: pyjwt dependency-version: 2.13.0

dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Update redis requirement from >=5.0.0 to >=8.1.0
  ([#28](https://github.com/bmartel/django-lightning/pull/28),
  [`028cdf9`](https://github.com/bmartel/django-lightning/commit/028cdf98baa9a326968bbd3149c6be0ab17fb00a))

Updates the requirements on [redis](https://github.com/redis/redis-py) to permit the latest version.
  - [Release notes](https://github.com/redis/redis-py/releases) -
  [Changelog](https://github.com/redis/redis-py/blob/master/CHANGES) -
  [Commits](https://github.com/redis/redis-py/compare/v5.0.0...v8.1.0)

--- updated-dependencies: - dependency-name: redis dependency-version: 8.1.0

dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Update sqlx requirement in /rust_core/crates/db_engine
  ([#20](https://github.com/bmartel/django-lightning/pull/20),
  [`8120d23`](https://github.com/bmartel/django-lightning/commit/8120d23c5278915345a01da848c4ae7d1bb24dc5))

Updates the requirements on [sqlx](https://github.com/launchbadge/sqlx) to permit the latest
  version. - [Changelog](https://github.com/transact-rs/sqlx/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/launchbadge/sqlx/compare/v0.8.0...v0.9.0)

--- updated-dependencies: - dependency-name: sqlx dependency-version: 0.9.0

dependency-type: direct:production ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Update django-stubs requirement from >=5.0.0 to >=6.0.7
  ([#25](https://github.com/bmartel/django-lightning/pull/25),
  [`dc6be4f`](https://github.com/bmartel/django-lightning/commit/dc6be4f3a2926332f2b5ccad1a44cd5941d0545e))

Updates the requirements on [django-stubs](https://github.com/typeddjango/django-stubs) to permit
  the latest version. - [Release notes](https://github.com/typeddjango/django-stubs/releases) -
  [Commits](https://github.com/typeddjango/django-stubs/compare/5.0.0...6.0.7)

--- updated-dependencies: - dependency-name: django-stubs dependency-version: 6.0.7

dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Update maturin requirement from >=1.5.0 to >=1.14.1
  ([#24](https://github.com/bmartel/django-lightning/pull/24),
  [`1c6fedb`](https://github.com/bmartel/django-lightning/commit/1c6fedbecff30a8af6de906491913716cf5d8c9e))

Updates the requirements on [maturin](https://github.com/pyo3/maturin) to permit the latest version.
  - [Release notes](https://github.com/pyo3/maturin/releases) -
  [Changelog](https://github.com/PyO3/maturin/blob/main/Changelog.md) -
  [Commits](https://github.com/pyo3/maturin/compare/v1.5.0...v1.14.1)

--- updated-dependencies: - dependency-name: maturin dependency-version: 1.14.1

dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Update mypy requirement from >=1.10.0 to >=2.3.0
  ([#30](https://github.com/bmartel/django-lightning/pull/30),
  [`c417bd4`](https://github.com/bmartel/django-lightning/commit/c417bd40ea2b5354a89c97b4a76537c57fcabaef))

Updates the requirements on [mypy](https://github.com/python/mypy) to permit the latest version. -
  [Changelog](https://github.com/python/mypy/blob/master/CHANGELOG.md) -
  [Commits](https://github.com/python/mypy/compare/v1.10.0...v2.3.0)

--- updated-dependencies: - dependency-name: mypy dependency-version: 2.3.0

dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Update pytest requirement from >=8.0.0 to >=9.1.1
  ([#27](https://github.com/bmartel/django-lightning/pull/27),
  [`c2218a4`](https://github.com/bmartel/django-lightning/commit/c2218a466b0ccd213f904c89214ab3a69c25e350))

Updates the requirements on [pytest](https://github.com/pytest-dev/pytest) to permit the latest
  version. - [Release notes](https://github.com/pytest-dev/pytest/releases) -
  [Changelog](https://github.com/pytest-dev/pytest/blob/main/CHANGELOG.rst) -
  [Commits](https://github.com/pytest-dev/pytest/compare/8.0.0...9.1.1)

--- updated-dependencies: - dependency-name: pytest dependency-version: 9.1.1

dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Update ruff requirement from >=0.5.0 to >=0.16.0
  ([#21](https://github.com/bmartel/django-lightning/pull/21),
  [`f0bbd90`](https://github.com/bmartel/django-lightning/commit/f0bbd90c795992904fdc598cf111db76e064e934))

Updates the requirements on [ruff](https://github.com/astral-sh/ruff) to permit the latest version.
  - [Release notes](https://github.com/astral-sh/ruff/releases) -
  [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/astral-sh/ruff/compare/0.5.0...0.16.0)

--- updated-dependencies: - dependency-name: ruff dependency-version: 0.16.0

dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Update setuptools requirement from >=61.0 to >=83.0.0
  ([#26](https://github.com/bmartel/django-lightning/pull/26),
  [`34ba706`](https://github.com/bmartel/django-lightning/commit/34ba706f40558e3d368056b1c29aa3a5ed6a599e))

Updates the requirements on [setuptools](https://github.com/pypa/setuptools) to permit the latest
  version. - [Release notes](https://github.com/pypa/setuptools/releases) -
  [Changelog](https://github.com/pypa/setuptools/blob/main/NEWS.rst) -
  [Commits](https://github.com/pypa/setuptools/compare/v61.0.0...v83.0.0)

--- updated-dependencies: - dependency-name: setuptools dependency-version: 83.0.0

dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>


## v0.18.1 (2026-07-30)

### Bug Fixes

- **k8s**: Resolve kube-linter security and resource rules in caddy-ingress.yaml
  ([`f448391`](https://github.com/bmartel/django-lightning/commit/f4483916e18bf4fcd015b2283a719ebb05cfa879))


## v0.18.0 (2026-07-30)

### Features

- **infra**: Add Caddy reverse proxy and Let's Encrypt automated SSL for Docker Compose and
  Kubernetes
  ([`09f896e`](https://github.com/bmartel/django-lightning/commit/09f896eff184587000090167816382a1ec53a246))


## v0.17.0 (2026-07-29)

### Documentation

- Overhaul README with realistic median benchmark metrics and clean typography
  ([`fec75ad`](https://github.com/bmartel/django-lightning/commit/fec75adecbbe8adb28cd40149a9c6bb9a6cd4379))

### Features

- Register article and native Rust version endpoints and update realtime stream text
  ([`d62c89b`](https://github.com/bmartel/django-lightning/commit/d62c89b9570ebf593aa3ade88ca45f0bcfe1e483))


## v0.16.0 (2026-07-29)

### Documentation

- Update AGENTS.md and README.md with new CLI commands and features
  ([`4a640cc`](https://github.com/bmartel/django-lightning/commit/4a640cc816cf81447a015fd09a78f48103874291))

### Features

- **rust_core**: Refactor to Pattern 3 Cargo Workspace Architecture by default
  ([`bf3b410`](https://github.com/bmartel/django-lightning/commit/bf3b410567f161808c0b4b0c7296d02082b3d169))


## v0.15.0 (2026-07-29)

### Features

- Add APIKey authentication helper and multi-auth dependency
  ([`2eb598a`](https://github.com/bmartel/django-lightning/commit/2eb598a28b9cce304d6dc1be90fc46d1f9c9b6a8))

### Refactoring

- Replace Organization with general Tenant model and remove async storage module
  ([`3f87f8e`](https://github.com/bmartel/django-lightning/commit/3f87f8eb7ab05e29e06054875ea33b7f7d205bd6))


## v0.14.0 (2026-07-29)

### Features

- Add multi-tenancy organizations, API keys, and async object storage baseline (Phase 3)
  ([`7054bbb`](https://github.com/bmartel/django-lightning/commit/7054bbbeb79087a89fbe0b50dc7fda0dc73714c1))


## v0.13.0 (2026-07-29)

### Features

- Add synthetic DB seeder, multi-service dev launcher, and correlation telemetry (Phase 2)
  ([`5d66e86`](https://github.com/bmartel/django-lightning/commit/5d66e86aae97c00438a2e25d4f7f0a9265b10699))


## v0.12.0 (2026-07-29)

### Features

- Expand MCP server tools, add async response caching, and resource generator CLI (Phase 1)
  ([`557c8b4`](https://github.com/bmartel/django-lightning/commit/557c8b44ec8da25d3120605f6f327369fcd9dc81))


## v0.11.0 (2026-07-29)

### Documentation

- **readme**: Add Rust DB Engine & model codegen documentation
  ([`3f3c601`](https://github.com/bmartel/django-lightning/commit/3f3c601bdbfffa69ae7b2873ccdcc5b021313530))

### Features

- Enhance agentic DX, type safety, health profiling, and CLI scaffolding parity
  ([`fe7a4f8`](https://github.com/bmartel/django-lightning/commit/fe7a4f8ae9d9884a70053ae3d8a77a7bfa9eecc4))


## v0.10.0 (2026-07-28)

### Features

- **rust**: Add Django-guided Rust DB engine with model codegen and sqlx integration
  ([`c9121a0`](https://github.com/bmartel/django-lightning/commit/c9121a0997b9555cc97d1a0417300451b4d0cf0e))


## v0.9.9 (2026-07-28)

### Bug Fixes

- **ci**: Add concurrency controls and git rebase step to semantic-release workflow to prevent race
  conditions
  ([`a6c32e7`](https://github.com/bmartel/django-lightning/commit/a6c32e790ac2aec0b207e6b39af31e9ff050eda3))


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
