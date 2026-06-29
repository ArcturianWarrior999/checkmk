#!groovy

/// file: winagt-test-integration.groovy

void main() {
    def windows = load("${checkout_dir}/buildscripts/scripts/utils/windows.groovy");

    stage("Run 'test_integration'") {
        dir("${checkout_dir}") {
            withNexusCredentials {
                windows.build(
                    TARGET: 'test_integration',
                    CREDS: NEXUS_USERNAME + ':' + NEXUS_PASSWORD,
                    CACHE_URL: 'https://artifacts.lan.tribe29.com/repository/omd-build-cache/'
                );
            }
        }
    }
}

return this;
