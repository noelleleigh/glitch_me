Get-ChildItem .\readme_assets -Filter *_small.png |
ForEach-Object{
    py -m glitch_me single $_.FullName .\readme_assets;
    py -m glitch_me gif $_.FullName .\readme_assets;
}
