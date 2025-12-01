import os
from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.menu_model import Menu
from app.models.item_category_model import ItemCategory
from app.repositories.menu_repository import MenuRepository


# Keep uploads under the app directory to align with the StaticFiles mount in main.py
BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "uploads" / "menu"


class MenuService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MenuRepository(db)

    async def _save_image(self, image: UploadFile | None) -> str | None:
        if not image:
            return None
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        ext = Path(image.filename).suffix or ""
        filename = f"{uuid4().hex}{ext}"
        file_path = UPLOAD_DIR / filename
        content = await image.read()
        file_path.write_bytes(content)
        # Store relative path so it can be served via /uploads
        return str(Path("uploads") / "menu" / filename)

    async def _remove_image(self, path: str | None):
        if path:
            absolute_path = (BASE_DIR / path).resolve()
        else:
            absolute_path = None
        if absolute_path and absolute_path.exists():
            try:
                os.remove(absolute_path)
            except OSError:
                pass

    async def create_menu(self, restaurant_id: int, data, image: UploadFile | None = None):
        await self.repo.ensure_restaurant(restaurant_id)
        await self.repo.ensure_category(data.item_category_id, restaurant_id)

        image_path = await self._save_image(image)

        menu = Menu(
            name=data.name,
            price=data.price,
            description=data.description,
            image=image_path,
            restaurant_id=restaurant_id,
            item_category_id=data.item_category_id,
        )
        return await self.repo.create_menu(menu)

    async def update_menu(self, menu_id: int, data, image: UploadFile | None = None):
        menu = await self.repo.get_menu_by_id(menu_id)
        if not menu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")

        if data.name is not None:
            menu.name = data.name
        if data.price is not None:
            menu.price = data.price
        if data.description is not None:
            menu.description = data.description
        if data.item_category_id is not None:
            await self.repo.ensure_category(data.item_category_id, menu.restaurant_id)
            menu.item_category_id = data.item_category_id

        if image is not None:
            new_path = await self._save_image(image)
            await self._remove_image(menu.image)
            menu.image = new_path

        return await self.repo.update_menu(menu)

    async def delete_menu(self, menu_id: int):
        menu = await self.repo.get_menu_by_id(menu_id)
        if not menu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
        await self._remove_image(menu.image)
        await self.repo.delete_menu(menu)
        return {"message": "Menu item deleted successfully"}

    async def get_menu_by_id(self, menu_id: int):
        menu = await self.repo.get_menu_by_id(menu_id)
        if not menu:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
        return menu

    async def get_menus_by_restaurant(self, restaurant_id: int, category_id: int | None = None):
        await self.repo.ensure_restaurant(restaurant_id)
        if category_id is not None:
            await self.repo.ensure_category(category_id, restaurant_id)
        return await self.repo.get_menus_by_restaurant(restaurant_id, category_id)

    async def get_menus_grouped_by_category(self, restaurant_id: int):
        await self.repo.ensure_restaurant(restaurant_id)
        categories_result = await self.db.execute(
            select(ItemCategory).where(ItemCategory.restaurant_id == restaurant_id)
        )
        categories = categories_result.scalars().all()

        groups = []
        for category in categories:
            menus = await self.repo.get_menus_by_restaurant(restaurant_id, category.id)
            groups.append({
                "category_id": category.id,
                "category_name": category.name,
                "items": menus
            })
        return groups
