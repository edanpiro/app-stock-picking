from fastapi import APIRouter, HTTPException
from app.models.stock_picking import StockPicking

import xmlrpc.client
import os


router = APIRouter(tags=["stock_picking"])

ODOO_URL = os.environ.get("ODOO_URL")
DB = os.environ.get("ODOO_DB")
USERNAME = os.environ.get("ODOO_USERNAME")
PASSWORD = os.environ.get("ODOO_PASSWORD")

common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

STOCK_PICKING_FIELDS = [
    "name", "scheduled_date", "state", "location_id", "location_dest_id",
    "picking_type_id", "move_type", "priority", "origin", "group_id", "partner_id",
    "scheduled_date", "date_done", "date_deadline", "date", "company_id", "note",
    "picking_type_code", "backorder_id", "origin"
]


def get_paginated_stock_pickings(domain=None, page=1, limit=10):
    if domain is None:
        domain = []
    offset = (page - 1) * limit
    total_count = models.execute_kw(DB, uid, PASSWORD, "stock.picking", "search_count", [domain])
    stock_ids = models.execute_kw(DB, uid, PASSWORD, "stock.picking", "search", [domain],
                                  {"offset": offset, "limit": limit})
    stock_picking = models.execute_kw(DB, uid, PASSWORD, "stock.picking", "read", [stock_ids],
                                      {"fields": STOCK_PICKING_FIELDS})
    
    next_page_link = None
    if offset + limit < total_count:
        next_page_link = f"/stock_picking/all?page={page + 1}"
    
    return {
        "count": len(stock_picking),
        "total_count": total_count,
        "page": page,
        "next_page_link": next_page_link,
        "results": stock_picking
    }


@router.get("/stock_picking/all")
def get_stock_picking(page: int = 1):
    """Returns paginated stock pickings."""
    return get_paginated_stock_pickings(domain=[], page=page)


@router.get("/stock_picking/incoming")
def get_stock_picking_in(page: int = 1):
    """Returns all incoming stock pickings."""
    return get_paginated_stock_pickings(domain=[("picking_type_id", "=", 1)], page=page)


@router.get("/stock_picking/outgoing")
def get_stock_picking_out(page: int = 1):
    """Returns all outgoing stock pickings."""
    return get_paginated_stock_pickings(domain=[("picking_type_id", "=", 2)], page=page)


@router.post("/stock_picking")
def create_stock_picking(stock_picking: StockPicking):
    """Creates a new stock picking and related moves."""
    picking_type_id = models.execute_kw(DB, uid, PASSWORD, "stock.picking.type", "search",
                                        [[["code", "=", stock_picking.picking_type]]])
    stock_id = models.execute_kw(DB, uid, PASSWORD, "stock.picking", "create", [{
        "partner_id": stock_picking.partner_id,
        "scheduled_date": stock_picking.scheduled_date,
        "picking_type_id": picking_type_id[0],
        "origin": stock_picking.origin,
    }])
    for move in stock_picking.moves:
        if stock_picking.picking_type == "incoming":
            location_id = 13
            location_dest_id = 8
        elif stock_picking.picking_type == "outgoing":
            location_id = 8
            location_dest_id = 5
        
        models.execute_kw(DB, uid, PASSWORD, "stock.move", "create", [{
            "product_id": move.product_id,
            "product_uom_qty": move.product_uom_qty,
            "picking_id": stock_id,
            "location_id": location_id,
            "location_dest_id": location_dest_id,
            "name": "Stock Move",
            "description_picking": move.description_picking,
            "quantity": move.quantity,
        }])
    
    models.execute_kw(DB, uid, PASSWORD, "stock.picking", "action_confirm", [stock_id])
    models.execute_kw(DB, uid, PASSWORD, "stock.picking", "action_assign", [stock_id])
    models.execute_kw(DB, uid, PASSWORD, "stock.picking", "button_validate", [stock_id])
    return {"stock_id": stock_id}