/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_2397634576")

  // update collection data
  unmarshal({
    "createRule": "user_id = @request.auth.id",
    "deleteRule": "",
    "listRule": "user_id = @request.auth.id",
    "updateRule": "",
    "viewRule": "user_id = @request.auth.id"
  }, collection)

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_2397634576")

  // update collection data
  unmarshal({
    "createRule": "@request.auth.id != \"\" && user_id = @request.auth.id",
    "deleteRule": null,
    "listRule": "@request.auth.id != \"\" && user_id = @request.auth.id",
    "updateRule": null,
    "viewRule": "@request.auth.id != \"\" && user_id = @request.auth.id"
  }, collection)

  return app.save(collection)
})
