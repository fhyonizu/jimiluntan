from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Category, Thread, Post
from app.forms import ThreadForm, PostForm, CategoryForm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    categories = Category.query.all()
    recent_threads = Thread.query.order_by(Thread.created_at.desc()).limit(10).all()
    return render_template('index.html', categories=categories, recent_threads=recent_threads)

@bp.route('/category/<int:category_id>')
def category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    threads = Thread.query.filter_by(category_id=category_id)\
        .order_by(Thread.updated_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    return render_template('category.html', category=category, threads=threads)

@bp.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    form = PostForm()
    
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('请先登录后再回复', 'warning')
            return redirect(url_for('auth.login'))
        
        post = Post(
            content=form.content.data,
            user_id=current_user.id,
            thread_id=thread.id
        )
        db.session.add(post)
        thread.updated_at = db.func.now()
        db.session.commit()
        flash('回复成功！', 'success')
        return redirect(url_for('main.thread', thread_id=thread.id))
    
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(thread_id=thread_id)\
        .order_by(Post.created_at.asc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('thread.html', thread=thread, posts=posts, form=form)

@bp.route('/thread/new', methods=['GET', 'POST'])
@login_required
def new_thread():
    form = ThreadForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        thread = Thread(
            title=form.title.data,
            content=form.content.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        db.session.add(thread)
        db.session.commit()
        flash('主题创建成功！', 'success')
        return redirect(url_for('main.thread', thread_id=thread.id))
    
    return render_template('new_thread.html', form=form)

@bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('分类创建成功！', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('new_category.html', form=form)
