Get-ChildItem .\readme_assets -Filter *_small.png |
ForEach-Object{
    py . single $_.FullName .\readme_assets;
    py . gif $_.FullName .\readme_assets;
}
