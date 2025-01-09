/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_591782289")

  // add field
  collection.fields.addAt(3, new Field({
    "hidden": false,
    "id": "number3807475020",
    "max": null,
    "min": null,
    "name": "scan_count",
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
  collection.fields.removeById("number3807475020")

  return app.save(collection)
})
