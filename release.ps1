poetry version $args[0]

git add pyproject.toml

$version = poetry version | Select-String '[0-9]+\.[0-9]+\.[0-9]+' -All | Select-Object -Expand Matches | ForEach-Object { $_.Value }

$versionString = "v$version"

Write-Output $versionString

git commit -m "$versionString"

git push

git tag $versionString

git push origin $versionString