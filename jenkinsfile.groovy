properties([
  parameters([
    choice(choices: ['patch','minor','major','tag','addon'], name: 'patchVersion', description: 'What needs to be bump?'),
    string(defaultValue:'', description: 'Force set newVersion or leave empty', name: 'newVersion', trim: false),
    string(defaultValue:'', description: 'Set grpcVersion or leave empty', name: 'grpcVersion', trim: false),
    choice(choices: ['local', 'global'], name: 'release', description: 'It\'s local release or global?'),
   ])
])

SERVICENAME = 'hydro-serving-cli'
SEARCHPATH = './requirements.txt'
SEARCHGRPC = 'hydro-serving-grpc'

def checkoutRepo(String repo){
  git changelog: false, credentialsId: 'HydroRobot_AccessToken', poll: false, url: repo
}

def getVersion(){
    try{
      if (params.release == 'global'){
        //remove all rc dev or post postfix and quotes
        version = sh(script: "cat \"version\" | sed 's/\\\"/\\\\\"/g' | sed -E 's/(-rc[0-9].*)|(.post[0-9].*)|(.dev[0-9].*)//g'", returnStdout: true ,label: "get version").trim()
      }else{
        //remove only quotes
        version = sh(script: "cat \"version\" | sed 's/\\\"/\\\\\"/g'", returnStdout: true ,label: "get version").trim()
      }
        return version
    }catch(e){
        return "file " + stage + "/version not found" 
    }
}

def bumpVersion(String currentVersion,String newVersion, String patch, String path){
    if (currentVersion =~ /\w*rc/ || newVersion =~ /\w*rc/){
      sh script: """cat <<EOF> ${WORKSPACE}/bumpversion.cfg
[bumpversion]
current_version = 0.0.0
commit = False
tag = False
parse = (?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)-?(?P<tag>\\w*rc)?(?P<addon>\\d+)?
serialize =
    {major}.{minor}.{patch}-{tag}{addon}
    {major}.{minor}.{patch}

[bumpversion:part:addon]

[bumpversion:part:tag]
optional_value = release
values =
  rc
  release

EOF""", label: "Set bumpversion configfile"
  }else if (currentVersion =~ /\w*post/ || newVersion =~ /\w*post/){
    sh script: """cat <<EOF> ${WORKSPACE}/bumpversion.cfg
[bumpversion]
current_version = 0.0.0
commit = False
tag = False
parse = (?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+).?(?P<tag>\\w*post)?(?P<addon>\\d+)?
serialize =
    {major}.{minor}.{patch}.{tag}{addon}
    {major}.{minor}.{patch}

[bumpversion:part:addon]

[bumpversion:part:tag]
optional_value = release
values =
  post
  release

EOF""", label: "Set bumpversion configfile"
  }else if (currentVersion =~ /\w*dev/ || newVersion =~ /\w*dev/){
    sh script: """cat <<EOF> ${WORKSPACE}/bumpversion.cfg
[bumpversion]
current_version = 0.0.0
commit = False
tag = False
parse = (?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+).?(?P<tag>\\w*dev)?(?P<addon>\\d+)?
serialize =
    {major}.{minor}.{patch}.{tag}{addon}
    {major}.{minor}.{patch}

[bumpversion:part:addon]

[bumpversion:part:tag]
optional_value = release
values =
  dev
  release

EOF""", label: "Set bumpversion configfile"
  }else{
    sh script: """cat <<EOF> ${WORKSPACE}/bumpversion.cfg
[bumpversion]
current_version = 0.0.0
commit = False
tag = False
parse = (?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)
serialize =
    {major}.{minor}.{patch}

EOF""", label: "Set bumpversion configfile"    
    }
    if (newVersion != null && newVersion != ''){
        sh("echo $newVersion > version") 
    }else{
        sh("bumpversion $patch $path --config-file '${WORKSPACE}/bumpversion.cfg' --allow-dirty --verbose --current-version '$currentVersion'")   
    }
}

//Собираем питонячие проекты, тестируем
def buildPython(String command, String version){
    configFileProvider([configFile(fileId: 'PYPIDeployConfiguration', targetLocation: "${env.WORKSPACE}/.pypirc", variable: 'PYPI_SETTINGS')]) {
      if(command == "build"){
        sh script:"""#!/bin/bash
        python3 -m venv venv &&
        source venv/bin/activate
        
        pip install wheel~=0.34.2 &&
        pip install setuptools==39.0.1 &&
        make PYTHON=python wheel &&
        make PYTHON=python3 test &&
        deactivate
        """, label: "Build python package"
      }else if(command == "release"){
        try{
        sh script: """#!/bin/bash
        python3 -m venv venv &&
        source venv/bin/activate
        
        pip install wheel~=0.34.2 &&
        pip install setuptools==39.0.1 &&
        pip install twine &&
        make PYTHON=python wheel &&
        make PYTHON=python test &&
        twine upload --config-file ${env.WORKSPACE}/.pypirc -r testpypi ${env.WORKSPACE}/dist/*""",label: "Release python package"
        }catch(err){
          echo "$err"
        }
        withCredentials([file(credentialsId: 'SonatypeSigningKey', variable: 'SONATYPE_KEY_PATH')]) {
          sh script: "gpg --import ${SONATYPE_KEY_PATH}", label: "Sign package"
          sh script: "mkdir -p ~/.sbt/gpg/ && chmod -R 777 ~/.sbt/gpg/"
          sh script: "cp ${SONATYPE_KEY_PATH} ~/.sbt/gpg/secring.asc"
          dir("scala-package"){
            try {
              //sh script: "sbt -DappVersion=$version 'set pgpPassphrase := Some(Array())'  +publishLocal", label: "publish local"
              sh script: "sbt -DappVersion=$version 'set pgpPassphrase := Some(Array())'  +publishSigned", label: "publish signed"
              sh script: "sbt -DappVersion=$version 'sonatypeReleaseAll'", label: "Release all"
            }catch(err){
              echo "$err"
            }
          }
        }
      }else{
        echo "command $command not found! Use build or release"
      }
    }
}

//Релиз сервисов, создаем коммиты и теги в гите
def releaseService(String xVersion, String yVersion){
  withCredentials([usernamePassword(credentialsId: 'HydroRobot_AccessToken', passwordVariable: 'password', usernameVariable: 'username')]) {
        //Set global git
      sh script: "git config --global user.name \"$username\"",label: "Set global username git"
      sh script: "git config --global user.email \"$username@provectus.com\"",label: "Set global email git"
      sh script: "git diff", label: "show diff"
      sh script: "git add .", label: "add all file to commit"
      sh script: "git commit -m 'Bump to $yVersion'", label: "commit to git"
      sh script: "git push --set-upstream origin master", label: "push all file to git"
      sh script: "git tag -a $yVersion -m 'Bump $xVersion to $yVersion version'",label: "set git tag"
      sh script: "git push --set-upstream origin master --tags",label: "push tag and create release"
  }
}


node('hydrocentral') {
    stage('SCM'){

      checkoutRepo("https://github.com/Hydrospheredata/$SERVICENAME" + '.git')
      if (params.grpcVersion == ''){
          //Set grpcVersion
          grpcVersion = sh(script: "curl -Ls https://pypi.org/pypi/hydro-serving-grpc/json | jq -r .info.version", returnStdout: true, label: "get grpc version").trim()
      }
    }

    stage('Test'){
      if (env.CHANGE_ID != null){
        currentVersion = getVersion()
        buildPython("build", currentVersion)
      }
    }

    stage('Release'){
      if (BRANCH_NAME == 'master' || BRANCH_NAME == 'main'){
        oldVersion = getVersion()
        bumpVersion(getVersion(),params.newVersion,params.patchVersion,'version')
        newVersion = getVersion()
        buildPython("build", newVersion)
        buildPython("release", newVersion)
        releaseService(oldVersion, newVersion)
      }
    }
}