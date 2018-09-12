def repository = 'hydro-serving-cli'


def buildAndPublishReleaseFunction={
    sh "sudo pip3 install --upgrade pip"
    sh "sudo pip3 install setuptools==39.0.1"
    sh "make PYTHON=python3 wheel"

    def curVersion = getVersion()

    sh "make PYTHON=python3 test"

    sh 'sudo pip3 install twine'
    configFileProvider([configFile(fileId: 'PYPIDeployConfiguration', targetLocation: '.pypirc', variable: 'PYPI_SETTINGS')]) {
        sh "twine upload --config-file ${env.WORKSPACE}/.pypirc -r pypi ${env.WORKSPACE}/dist/*"
    }
}

def buildFunction={
    sh "sudo pip3 install --upgrade pip"
    sh "sudo pip3 install setuptools==39.0.1"
    sh "make PYTHON=python3 wheel"
    sh "make PYTHON=python3 test"
}

def collectTestResults = {
    junit testResults: 'test-report.xml', allowEmptyResults: true
}

pipelineCommon(
        repository,
        false, //needSonarQualityGate,
        [],
        collectTestResults,
        buildAndPublishReleaseFunction,
        buildFunction,
        buildFunction
)