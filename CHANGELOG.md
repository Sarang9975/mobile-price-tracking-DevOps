# Changelog

All notable changes to the Mobile Price Predictor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Docker support with Dockerfile and docker-compose.yml
- GitHub Actions CI/CD pipeline
- Comprehensive test suite
- Makefile for common development tasks
- API documentation
- Deployment script
- Environment configuration management

### Changed
- Improved error handling and validation
- Enhanced logging throughout the application
- Refactored code structure with utility modules
- Updated dependencies to latest stable versions

## [2.1.0] - 2024-11-19

### Added
- Comprehensive input validation for all features
- Structured logging with configurable log levels
- Feature range validation (battery power, RAM, clock speed)
- Improved error messages and user feedback
- Configuration management with environment variables

### Changed
- Enhanced error handling with specific exception types
- Better user experience with detailed validation messages
- Improved code maintainability with type hints

## [2.0.0] - 2024-11-19

### Added
- Configuration management with dedicated config.py module
- Utility functions for data validation and preprocessing
- Type hints for better code maintainability
- Environment-based configuration

### Changed
- Refactored application structure
- Separated concerns into dedicated modules
- Updated requirements.txt with specific versions

## [1.0.0] - 2024-11-19

### Added
- Initial Flask web application
- AWS SageMaker integration for ML predictions
- Responsive web interface
- Support for 20 mobile phone features
- Four price category predictions (Budget, Lower Mid-range, Upper Mid-range, Premium)

### Features
- Interactive form for mobile specifications
- Real-time price category prediction
- Visual feedback with category images
- Mobile-friendly responsive design 