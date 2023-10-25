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

## A note on container deployment
Due to the large size of the ML models, they aren't checked into git.  Also due to the large model size, they aren't part of the container build process.  The container loads them out of a Docker volume (created externally with `docker volume create metadata_models`), and the models need to be manually copied into the Docker volume for the modelserver to function properly, e.g.

```
docker cp opencontext-material isamples_modelserver-isamples_modelserver-1:/app/metadata_models/
```

Once this is done, you can simply start up the container like so:

```
docker compose up --build
```

## Volume contents
Once the app is running, the `metadata_models` directory should look like this:

```
root@1b915258a2ba:/app/metadata_models# ls -la
total 149520
drwxrwxr-x 3 root   root       4096 Oct 25 23:32 .
drwxr-xr-x 1 root   root       4096 Oct 25 23:15 ..
-rwxr-xr-x 1 100216 10013       342 Dec 16  2022 OPENCONTEXT_material_config.json
-rwxr-xr-x 1 100216 10013       238 Dec 16  2022 OPENCONTEXT_sample_config.json
-rwxr-xr-x 1 100216 10013       421 Dec 16  2022 SESAR_material_config.json
drwxr-xr-x 5 root   root       4096 Oct 25 23:34 models
-rw-rw-r-- 1   1001  1001 153078525 Mar  4  2022 sampledFeature.bin
root@1b915258a2ba:/app/metadata_models# ls -la models/
total 20
drwxr-xr-x 5 root   root  4096 Oct 25 23:34 .
drwxrwxr-x 3 root   root  4096 Oct 25 23:32 ..
drwxr-xr-x 2 100216 10013 4096 Dec 15  2022 opencontext-material
drwxr-xr-x 2 100216 10013 4096 Jan 24  2023 opencontext-sample
drwxr-xr-x 2 100216 10013 4096 Sep 23  2022 sesar-material
```