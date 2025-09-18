from aredis_om.model.model import NotFoundError
import pytest

from src.fifi import LoggerFactory, RedisBaseModel


LOGGER = LoggerFactory().get(__name__)


class Product(RedisBaseModel):
    name: str
    price: float
    quantity: int


@pytest.mark.redis
@pytest.mark.asyncio
async def test_save():
    prod = await Product.create(pk="product_1", name="Gadget", price=49.99, quantity=5)
    await prod.save()

    assert prod.pk is not None
    fetched = await Product.get_by_id(prod.pk)
    LOGGER.info(f"Fetched:{fetched.model_dump()}")

    assert fetched.pk == prod.pk
    assert fetched.price == prod.price
    assert fetched.quantity == prod.quantity
    assert fetched.name == prod.name


@pytest.mark.redis
@pytest.mark.asyncio
async def test_update():
    prod = await Product.create(pk="product_1", name="Gadget", price=49.99, quantity=5)
    await prod.save()

    await prod.update(price=50)
    assert prod.pk is not None

    fetched = await Product.get_by_id(prod.pk)
    LOGGER.info(f"Fetched Update:{fetched.model_dump()}")

    assert fetched.pk == prod.pk
    assert fetched.price == prod.price
    assert fetched.quantity == prod.quantity
    assert fetched.name == prod.name
    assert fetched.created_at is not None
    assert fetched.updated_at is not None
    assert fetched.created_at.timestamp() < fetched.updated_at.timestamp()


@pytest.mark.redis
@pytest.mark.asyncio
async def test_delete():
    prod = await Product.create(pk="product_1", name="Gadget", price=49.99, quantity=5)
    await prod.save()

    await prod.delete()
    assert prod.pk is not None

    with pytest.raises(NotFoundError):
        fetched = await Product.get_by_id(prod.pk)
        LOGGER.info(f"Fetched deleted:{fetched.model_dump()}")
