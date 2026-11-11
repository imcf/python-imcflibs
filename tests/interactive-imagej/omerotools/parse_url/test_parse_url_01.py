# @ String (label="OMERO HOST") host
# @ Integer (label="OMERO PORT", value=4064) port
# @ String (label="OMERO User") user
# @ String (label="OMERO Password", style="password") pwd
# @ String (label="Provide OMERO Project URL") url_project
# @ String (label="Provide OMERO 'Dataset A' URL") url_dataset
# @ String (label="Provide OMERO URL for ALL images in 'Dataset A'") url_images
# Examples
# url_project: https://omero.biozentrum.unibas.ch/webclient/?show=project-25155
# url_dataset: https://omero.biozentrum.unibas.ch/webclient/?show=dataset-82170
# url_images: https://omero.biozentrum.unibas.ch/webclient/?show=image-3454870|image-3454871|image-3454872|image-3454873|image-3454874


from imcflibs.imagej import omerotools

# Parse the url_images to get the IDs
image_ids = []
parts = url_images.split("|")
for part in parts:
    if "image-" in part:
        image_id = part.split("image-")[1].split("/")[0]
        image_ids.append(image_id)
assert len(image_ids) > 0, "No image ids in image url!"

# Test
try:
    user_client = omerotools.connect(host, port, user, pwd)

    # Project URLs are not implemented
    ids = None
    try:
        ids = omerotools.parse_url(user_client, url_project)
    except NotImplementedError:
        pass
    assert ids is None

    # Single Dataset
    ids = omerotools.parse_url(user_client, url_dataset)
    assert len(ids) == len(image_ids)

    # Images url
    ids = omerotools.parse_url(user_client, url_images)
    assert len(ids) == len(image_ids)
    for cur_id in ids:
        cur_id = cur_id.getId()
        assert str(cur_id) in image_ids

    # Image IDs as comma-separated string
    ids = omerotools.parse_url(user_client, ",".join(image_ids))
    assert len(ids) == len(image_ids)
    for cur_id in ids:
        cur_id = cur_id.getId()
        assert str(cur_id) in image_ids
finally:
    if user_client is not user_client:
        user_client.disconnect()

print("Test completed!")
