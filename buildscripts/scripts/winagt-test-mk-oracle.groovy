#!groovy

/// file: winagt-test-mk-oracle.groovy

void main() {
    dir("${checkout_dir}/packages/mk-oracle") {
        withCredentials([
            string(
                credentialsId: "CI_ORA_WIN_TEST_PASSWORD",
                variable: "CI_ORA_WIN_TEST_PASSWORD"),
        ]) {
            stage("Run mk-oracle component tests (network)") {
                // Target the Windows-native Oracle 23ai Free over TCP by pre-setting
                // CI_ORA2_DB_TEST; run.ps1 consumes it as-is.
                def winDbEndpoint = "oracle-win-ci.lan.checkmk.net:system:%CI_ORA_WIN_TEST_PASSWORD%:1521:_::FREE:FREE:_:";
                bat("set \"CI_ORA2_DB_TEST=${winDbEndpoint}\" && call run.cmd --component-tests");
            }
            withCredentials([
                sshUserPrivateKey(
                    credentialsId: "jenkins-oracle-win-ssh-key",
                    keyFileVariable: "CI_ORA_WIN_SSH_KEYFILE",
                    usernameVariable: "CI_ORA_WIN_REMOTE_USER"),
            ]) {
                stage("Run mk-oracle component tests (local, on Oracle host)") {
                    // Ship the test binary to the Oracle host and run it there
                    // against its local DB, covering host-local paths. The
                    // remote dir is unique per build so overlapping runs on
                    // the shared host cannot clobber each other's staging.
                    bat("set \"CI_ORA_WIN_REMOTE_DIR=C:\\ci\\%BUILD_TAG%\" && call run.cmd --remote-host");
                }
            }
        }
    }
}

return this;
