/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_2397634576")

  // update collection data
  unmarshal({
    "listRule": "@request.auth.id != \"\" && user_id = @request.auth.id"
  }, collection)

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_2397634576")

  // update collection data
  unmarshal({
    "listRule": null
  }, collection)

  return app.save(collection)
})
