/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_591782289")

  // add field
  collection.fields.addAt(4, new Field({
    "hidden": false,
    "id": "number27551843",
    "max": null,
    "min": null,
    "name": "box_size",
    "onlyInt": false,
    "presentable": false,
    "required": false,
    "system": false,
    "type": "number"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_591782289")

  // remove field
  collection.fields.removeById("number27551843")

  return app.save(collection)
})
