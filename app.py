from math import ceil
from sys import maxsize
from typing import Optional

from flask import Flask, render_template, abort, request
from werkzeug.exceptions import NotFound

from dao import ProductDao, Filtration

# создание приложения
app = Flask(__name__)


@app.route('/')
def show_all_products() -> str:
    """
    Показываем все продукты безо всяких условий
    """
    products: list = ProductDao.get_all_products()
    return render_template('show-all-products.html', products=products)


@app.route('/search/')
def search_products() -> str:
    """
    Показываем продукты, которые соответствуют присланным в запросе условиям
    """
    product_filtration = Filtration() \
        .equal('id', request.args.get('id', ''), 255) \
        .like('name', request.args.get('name', ''), 255) \
        .like('ean', request.args.get('ean', ''), 255) \
        .greater_equal('price', request.args.get('price_gte', ''), 255) \
        .less_equal('price', request.args.get('price_lte', ''), 255)

    products: list = ProductDao.get_products_with_filtration(product_filtration)
    return render_template('search-products.html', products=products)


@app.route('/product/<int:product_id>')
def show_single_product(product_id: int) -> str:
    """
    Показываем один конкретный продукт
    """

    # пришло слишком большое число - скажем пользователю, что был отправлен неправильный запрос
    if product_id > maxsize:
        abort(422)

    product: Optional[dict] = ProductDao.get_single_product(product_id)

    # если продукт по запрошенному идентификатору не найден - вернем 404 ошибку (данные не найдены)
    if product is None:
        abort(404)

    return render_template('show-single-product.html', product=product)


@app.route('/pages/', defaults={'page': 1})
@app.route('/pages/<int:page>')
def split_products_by_pages(page: int) -> str:
    """
    Показываем продукты по несколько штук на странице (с использованием постраничной навигации)
    """

    # получим общее количество продуктов и посчитаем, сколько у нас вообще может быть страниц
    products_qty = ProductDao.get_products_qty()
    qty_per_page = 2
    pages = ceil(products_qty / qty_per_page)

    # если номер пришедшей страницы слишком маленький или слишком большой - вернем 404 ошибку (данные не найдены)
    if page < 1 or page > pages:
        abort(404)

    current_offset = (page - 1) * qty_per_page
    products = ProductDao.get_products_with_limit_and_offset(qty_per_page, current_offset)

    return render_template(
        'split-products-by-pages.html', pages=pages, qty_per_page=qty_per_page, page=page, products=products)


@app.errorhandler(404)
def handle_not_found_page(error: NotFound) -> tuple:
    """
    Обработчик ненайденных страниц
    """
    return render_template('404.html'), 404


if __name__ == '__main__':
    # запуск приложения
    app.run(port=8001, debug=True)
