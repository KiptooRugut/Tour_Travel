from flask import Flask, render_template, flash, redirect, url_for, abort, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from ..models import Comment, User, Post, Upvote, Downvote
from .forms import UpdateProfile, PostForm, CommentForm
from flask_login import login_required, current_user
from flask_wtf.csrf import CSRFProtect, CSRFError
from passlib.hash import sha256_crypt
from functools import wraps
from .. import db, photos
from . import main
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from ..models import Post
from .. import db,create_app


class Post(ModelView):
    datamodel = SQLAInterface(Post, db.session)

    list_title = "List Contacts"
    show_title = "Show Contact"
    add_title = "Add Contact"
    edit_title = "Edit Contact"

    # list_widget = ListThumbnail

    label_columns = {
        "person_group_id": "Group",
        "photo_img": "Photo",
        "photo_img_thumbnail": "Photo",
    }
    list_columns = [
        "photo_img_thumbnail",
        "name",
        "personal_celphone",
        "business_celphone",
        "birthday",
        "person_group",
    ]

    show_fieldsets = [
        ("Summary", {"fields": ["photo_img", "name", "address", "person_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                    "personal_email",
                ],
                "expanded": False,
            },
        ),
        (
            "Professional Info",
            {
                "fields": [
                    "business_function",
                    "business_phone",
                    "business_celphone",
                    "business_email",
                ],
                "expanded": False,
            },
        ),
        ("Extra", {"fields": ["notes"], "expanded": False}),
    ]

    add_fieldsets = [
        ("Summary", {"fields": ["name", "photo", "address", "person_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "personal_phone",
                    "personal_celphone",
                    "personal_email",
                ],
                "expanded": False,
            },
        ),
        (
            "Professional Info",
            {
                "fields": [
                    "business_function",
                    "business_phone",
                    "business_celphone",
                    "business_email",
                ],
                "expanded": False,
            },
        ),
        ("Extra", {"fields": ["notes"], "expanded": False}),
    ]

    edit_fieldsets = [
        ("Summary", {"fields": ["name", "photo", "address", "person_group"]}),
        (
            "Personal Info",
            {
                "fields": [
                    "birthday",
                    "personal_phone",
                    "personal_celphone",
                    "personal_email",
                ],
                "expanded": False,
            },
        ),
        (
            "Professional Info",
            {
                "fields": [
                    "business_function",
                    "business_phone",
                    "business_celphone",
                    "business_email",
                ],
                "expanded": False,
            },
        ),
        ("Extra", {"fields": ["notes"], "expanded": False}),
    ]

# Views

@main.route('/user/<uname>')
def profile(uname):
    user = User.query.filter_by(username=uname).first()
    if user is None:
        abort(404)
    return render_template("profile/profile.html", user=user)


@main.route('/user/<uname>/update', methods=['GET', 'POST'])
@login_required
def update_profile(uname):
    user = User.query.filter_by(username=uname).first()
    if user is None:
        abort(404)
    form = UpdateProfile()
    if form.validate_on_submit():
        user.bio = form.bio.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('.profile', uname=user.username))
    return render_template('profile/update.html', form=form)


@main.route('/user/<uname>/update/pic', methods=['POST'])
@login_required
def update_pic(uname):
    user = User.query.filter_by(username=uname).first()
    if 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        path = f'photos/{filename}'
        user.profile_pic_path = path
        db.session.commit()
    return redirect(url_for('main.profile', uname=uname))


@main.route('/comment', methods=['GET', 'POST'])
@login_required
def add_comment():
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(name=form.name.data)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully.')
        return redirect(url_for('.index'))
    return render_template('comment.html', form=form)


@main.route('/post', methods=['GET', 'POST'])
@login_required
def new_post():
    post_form = PostForm()
    if post_form.validate_on_submit():
        title = post_form.post_title.data
        category = post_form.post_category.data
        content = post_form.post_content.data
        new_post = Post(title=title, content=content,
                        user=current_user, category=category)
        new_post.save_post()
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('main.index'))

    else:
        all_posts = Post.query.order_by(Post.date_posted).all()

    return render_template('posts.html', posts=all_posts, post_form=post_form)


@main.route('/post/<id>', methods=['GET', 'POST'])
@login_required
def post_details(id):
    comments = Comment.query.filter_by(post_id=id).all()
    posts = Post.query.get(id)
    if posts is None:
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            comment=form.comment.data,
            post_id=id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        form.comment.data = ''
        flash('Your comment has been posted successfully!')
    return render_template('comment.html', post=posts, comment=comments, comment_form=form)


# @main.route('/like/<int:id>', methods=['GET', 'POST'])
# @login_required
# def like(id):
#     post = Post.query.get(id)
#     if post is None:
#         abort(404)
#     like = Upvote.query.filter_by(user_id=current_user.id, post_id=id).first()
#     if like is not None:
#         db.session.delete(like)
#         db.session.commit()
#         flash('You have successfully unupvoted the pitch!')
#         return redirect(url_for('main.index'))
#     new_like = Upvote(
#         user_id=current_user.id,
#         post_id=id
#     )
#     db.session.add(new_like)
#     db.session.commit()
#     flash('You have successfully upvoted the pitch!')
#     return redirect(url_for('main.index'))


@main.route('/dislike/<int:id>', methods=['GET', 'POST'])
@login_required
def dislike(id):
    posts = Post.query.get(id)
    if posts is None:
        abort(404)
    
    dislike = Downvote.query.filter_by(
        user_id=current_user.id, post_id=id).first()
    if dislike is not None:
       
        db.session.delete(dislike)
        db.session.commit()
        flash('You have successfully undownvoted the pitch!')
        return redirect(url_for('.index'))

    new_dislike = Downvote(
        user_id=current_user.id,
        post_id=id
    )
    db.session.add(new_dislike)
    db.session.commit()
    flash('You have successfully downvoted the pitch!')
    return redirect(url_for('.index'))

# Views

@main.route('/')
def index():
    title = 'Welcome to Africa'
    return render_template('index.html', title=title)

def index():
    '''
    View root page function that returns the index page and its data.
    '''
    post_form = PostForm()
    all_posts = Post.query.order_by(Post.date_posted).all()
    return render_template('index.html', posts = all_posts)


@main.route('/carhire.html')
def carhire():
    return render_template('carhire.html')


@main.route('/contact.html')
def contact():
    return render_template('contact.html')


@main.route('/destinations.html')
def destinations():
    return render_template('destinations.html')


@main.route('/destinations/tsavo.html')
def tsavo():
    return render_template('destinations/tsavo.html')


@main.route('/destinations/tsavoeast.html')
def tsavoeast():
    return render_template('destinations/tsavoeast.html')


@main.route('/destinations/tanzania.html')
def tanzania():
    return render_template('destinations/tanzania.html')


@main.route('/destinations/samburu.html')
def samburu():
    return render_template('destinations/samburu.html')


@main.route('/destinations/nairobi.html')
def nairobi():
    return render_template('destinations/nairobi.html')


@main.route('/destinations/kilimanjaro.html')
def kilimanjaro():
    return render_template('destinations/kilimanjaro.html')


@main.route('/destinations/mtkenya.html')
def mtkenya():
    return render_template('destinations/mtkenya.html')


@main.route('/destinations/mara.html')
def mara():
    return render_template('destinations/mara.html')


@main.route('/destinations/nakuru.html')
def nakuru():
    return render_template('destinations/nakuru.html')


@main.route('/details/amboseli.html')
def amboseli():
    return render_template('details/amboseli.html')


@main.route('/details/tsavoamboseli.html')
def tsavoamboseli():
    return render_template('details/tsavoamboseli.html')


@main.route('/details/tsavoeast.html')
def tsaveast():
    return render_template('details/tsavoeast.html')


@main.route('/details/tsavomara.html')
def tsavomara():
    return render_template('details/tsavomara.html')


@main.route('/details/samburudetail.html')
def samburudetail():
    return render_template('details/samburudetail.html')


@main.route('/details/pejeta.html')
def pejeta():
    return render_template('details/pejeta.html')


@main.route('/details/giraffe.html')
def giraffe():
    return render_template('details/giraffe.html')


@main.route('/details/big5.html')
def big5():
    return render_template('details/big5.html')


@main.route('/details/bogoria.html')
def bogoria():
    return render_template('details/bogoria.html')


@main.route('/details/aberdares.html')
def aberdares():
    return render_template('details/aberdares.html')


@main.route('/details/nakurukenya.html')
def nakurukenya():
    return render_template('details/nakurukenya.html')


@main.route('/details/sirimon.html')
def sirimon():
    return render_template('details/sirimon.html')


@main.route('/details/hellsgate.html')
def hellsgate():
    return render_template('/details/hellsgate.html')


@main.route('/details/oldonyo.html')
def oldonyo():
    return render_template('/details/oldonyo.html')
