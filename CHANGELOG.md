# Changelog

## 0.5.3 - 2026-03-04

## Changed

- Updated get rates endpoint to new path `/rates` since `/rate` will be deprecated

## 0.5.2 - 2026-01-15

## Added

- Default timeout for network requests; set via environment variable
- Allow clients to override timeout for network requests
- Add #get_rates to crawl_client

## 0.5.1 - 2026-01-14

### Added

- Log scrubber for Authentication headers

### Changed

- Update self reporting to only require license id for custom licenses

## 0.5.0 - 2026-01-07

### Added

- Added async clients

### Changed

- Renamed module `licences` to `licenses` to use correct spelling

## 0.4.0 - 2026-01-05

### Added

- Add Search to SDK

### Changed

 - Update reporting to use V2 API
 - Update content catalog to use V2 API
 - Update rate to use V2 API
 - Updated api objects to use camel case names

## 0.3.0 - 2025-12-12

### Added

- Added self reporting

### Changed

- Update crawl content to support multiple formats
- Updated get content requests to use content format header
- Made format constant names more consistent

### Fixed

- Fix rates calls for V1 API

## 0.2.1 - 2025-12-01

### Added

- Added type hints

### Changed

- Updated get content apis to use V2 routes

## 0.2.0 - 2025-11-18

### Added

- Added crawl_client
  - Added get_content_catalog
  - Added crawl_content

### Fixed

- Updated get_rate to include api key in header

## 0.1.1 - 2025-11-12

### Added

- Add __version__ to module

### Fixed

- Fix examples not importing modules correctly
- Fix missing pydantic dependencies

## 0.1.0 - 2025-11-12

_Initial Release_