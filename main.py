from fastapi import FastAPI, HTTPException
from inventory_core import add_item, issue_item, return_item, get_status

app = FastAPI(title="Stock SaaS API")


@app.post("/items/add")
def api_add_item(name: str, quantity: int, threshold: int = 0):
    item = add_item(name, quantity, threshold)
    return {"message": f"Added {quantity} {name}(s)", "item": item}


@app.post("/items/issue")
def api_issue_item(name: str, quantity: int):
    try:
        item = issue_item(name, quantity)
        return {"message": f"Issued {quantity} {name}(s)", "item": item}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/items/return")
def api_return_item(name: str, quantity: int):
    try:
        item = return_item(name, quantity)
        return {"message": f"Returned {quantity} {name}(s)", "item": item}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/items/status")
def api_get_status(name: str | None = None):
    data = get_status(name)
    if not data:
        raise HTTPException(status_code=404, detail="Item not found" if name else "No items found")
    return data
