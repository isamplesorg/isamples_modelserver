# isamples_modelserver
REST API for invoking iSamples ML models

## A note on TorchVision installation
Due to the cuda binaries not existing on macOS, the installation process is a little goofy.  If we just use the standard poetry dependency specification, we end up with an unusable python environment on Linux.  To work around this issue, the poetry  dependencies only apply to macOS, e.g.:

```
torch = [
    { platform = "darwin", version = "^2.0.1" }
]
```

Then, on Linux we manually specify the archive URL and install via pip like this:


```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

In theory, poetry should be able to specify a different source and only use it for those dependencies.  However, when I tried that approach, it appeared to be trying to pull down binaries for every version of python and every operating system and took > 15 minutes to pull things down.  In light of this, we are using the workaround to manually install via `pip` which doesn't appear to exhibit this undesirable behavior.