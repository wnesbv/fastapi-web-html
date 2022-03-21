
from models.mls.user import Item
from schemas.user import ItemCreate

from sqlalchemy.orm import Session


def create_new_item(
    obj_in: ItemCreate,
    db: Session,
    owner_item_id: int
):

    item_obj = Item(**obj_in.dict(),
        owner_item_id = owner_item_id,
    )

    db.add(item_obj)
    db.commit()
    db.refresh(item_obj)

    return item_obj


def update_item(
    id: int,
    item: ItemCreate,
    db: Session,
    owner_item_id,
):

    existing_item = db.query(Item).filter(Item.id == id)

    if not existing_item.first():
        return False

    item.__dict__.update(
        owner_item_id=owner_item_id
    )
    existing_item.update(item.__dict__)
    db.commit()

    return existing_item


def item_delete(
    id: int,
    db: Session,
    owner_item_id,
):

    existing_item = db.query(Item).filter(Item.id == owner_item_id)

    if not existing_item.first():
        return False

    existing_item.delete(synchronize_session=False)
    db.commit()

    return True


# ...

def list_item(db: Session):

    obj_list = db.query(Item).all()

    return obj_list


def retreive_item(
    id: int,
    db: Session
):

    obj = db.query(Item).filter(Item.id == id).first()

    return obj


# ...

def search_item(
    query: str,
    db: Session
):

    obj_list = (
        db.query(Item).filter(Item.title.contains(query))
    )

    return obj_list
