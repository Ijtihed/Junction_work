/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_591782289")

  // update collection data
  unmarshal({
    "listRule": null
  }, collection)

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_591782289")

  // update collection data
  unmarshal({
    "listRule": "@request.auth.id = owner"
  }, collection)

  return app.save(collection)
})
