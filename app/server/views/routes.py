import uuid
from flask import (
    Blueprint,
    request,
    render_template,
    url_for,
    flash,
    redirect,
    jsonify,
    session,
)
from flask_login import current_user, login_required
from flask_mail import Message
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import or_, and_
from ..models.enums import NFTStatus
from ..config.database import db
from ..models.Ether import Ether
from ..models.NFT import NFT
from ..models.NFTViews import NFTViews
from ..models.Contact import Contact
from ..views.forms import SearchForm, ContactForm
from server import mail
from ..utils.helpers import send_dynamic_mail


mintverse = Blueprint("mintverse", __name__)


@mintverse.context_processor
def inject_search_form():
    form = SearchForm()
    return dict(form=form)


# HOME PAGE ROUTE (VIEW)
@mintverse.get("/")
# @login_required
def home_page():
    search_form = SearchForm()

    return render_template(
        "index.html",
        title="Home | MintVerse",
        current_user=current_user,
        search_form=search_form,
    )


# ABOUT PAGE ROUTE (VIEW)
@mintverse.get("/about")
def about_page():
    return render_template(
        "main/pages/nav/about-page.html", title="About Us | MintVerse"
    )


# TERMS AND CONDITIONS PAGE ROUTE (VIEW)
@mintverse.get("/terms_and_conditions")
def termsandcond_page():
    return render_template(
        "main/pages/nav/TandC-page.html", title="Ts & Cs | MintVerse"
    )


# FAQ PAGE ROUTE (VIEW)
@mintverse.get("/faq")
def faq_page():
    return render_template("main/pages/nav/faq-page.html", title="Faq | MintVerse")


# CONTACT PAGE ROUTE (VIEW)
@mintverse.route("/contact", methods=["GET", "POST"])
def contact_page():
    form = ContactForm()

    if request.method == "POST" and form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message = form.message.data

        # Validate email
        try:
            valid_email = validate_email(email)
            email = valid_email.normalized
        except EmailNotValidError as e:
            flash(f"Invalid email format: {e}", "danger")
            return redirect(url_for("mintverse.contact_page"))

        try:
            # Save contact message to the database
            contact_message = Contact(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )
            db.session.add(contact_message)
            db.session.commit()

            # Compose the email
            company_email = "support@mintverse.com"  # Replace with your company's email
            plain_text = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            html_content = f"""
            <html>
              <body>
                <h2>Contact Form Submission</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Subject:</strong> {subject}</p>
                <p><strong>Message:</strong><br>{message}</p>
              </body>
            </html>
            """

            # Send the email using the dynamic util
            send_dynamic_mail(
                subject=f"Contact Form Submission: {subject}",
                recipient=company_email,
                sender=email,
                plain_text=plain_text,
                html_content=html_content,
                smtp_user="support@mintverse.com",  # Use your SMTP user
                smtp_password="your_app_password",  # Use your SMTP password
            )

            flash(
                "Your message has been sent successfully! We will get back to you shortly.",
                "success",
            )
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while submitting your message: {e}", "danger")

        return redirect(url_for("mintverse.contact_page"))

    return render_template(
        "main/pages/nav/contact-page.html",
        title="Contact Us | MintVerse",
        form=form,
    )


# CATEGORY PAGE ROUTE (VIEW)
@mintverse.get("/category")
def category_page():
    return render_template(
        "main/pages/category-page.html",
        title="Explore Categories | MintVerse",
        current_user=current_user,
    )


# EXPLORE PAGE ROUTE (VIEW)
@mintverse.get("/explore")
def explore_page():
    return render_template(
        "main/pages/explore-page.html",
        title="All Collections | MintVerse",
        current_user=current_user,
    )


# NFT API ENDPOINT
@mintverse.get("/api/nfts/")
def get_nfts():
    nfts = NFT.query.all()
    return jsonify([nft.data() for nft in nfts])


# HERO API ENDPOINT (VIEW)
@mintverse.get("/hero/api/nfts/")
def get_hero_nfts():
    # ✅ Dynamically get all unique categories stored in the DB
    categories = db.session.query(NFT.category).distinct().all()
    categories = [c[0] for c in categories]  # Convert tuples to a simple list

    selected_nfts = []
    for category in categories:
        nft = (
            NFT.query.filter(
                and_(NFT.category == category, NFT.status == NFTStatus.AVAILABLE)
            )
            .offset(4)
            .first()
        )  # ✅ Get 5th item
        if nft:  # Ensure category has at least five NFTs
            selected_nfts.append(nft)

    # ✅ Handle empty results case
    if not selected_nfts:
        return jsonify(
            {"error": "No NFTs found with at least 5 listed items in each category"}
        )

    return jsonify(
        [n.data() for n in selected_nfts]
    )  # ✅ Send selected NFTs as JSON response


# HERO API ENDPOINT (VIEW)
@mintverse.get("/bsl/api/nfts/")
def get_bsl_nfts():
    # ✅ Dynamically get all unique categories stored in the DB
    categories = db.session.query(NFT.category).distinct().all()
    categories = [c[0] for c in categories]  # Convert tuples to a simple list

    selected_nfts = []
    for category in categories:
        nft = (
            NFT.query.filter(
                and_(NFT.category == category, NFT.status == NFTStatus.AVAILABLE)
            )
            .offset(2)
            .first()
        )  # ✅ Get 3rd item
        if nft:  # Ensure category has at least three NFTs
            selected_nfts.append(nft)

    # ✅ Handle empty results case
    if not selected_nfts:
        return jsonify(
            {"error": "No NFTs found with at least 3 listed items in each category"}
        )

    return jsonify(
        [n.data() for n in selected_nfts]
    )  # ✅ Send selected NFTs as JSON response


# TTP API ENDPOINT (VIEW)
@mintverse.get("/ttp/api/nfts/")
def get_ttp_nfts():
    categories = ["digital-art", "3d-art", "generative-art", "comic-art"]

    selected_nfts = []
    for category in categories:
        nft = NFT.query.filter(
            and_(
                NFT.category == category, NFT.status == NFTStatus.AVAILABLE
            )  # ✅ Correct Enum reference
        ).first()  # ✅ Get first NFT in each category
        if nft:  # Ensure the category has at least one NFT
            selected_nfts.append(nft)

    # ✅ Handle empty results case
    if not selected_nfts:
        return jsonify({"error": "No NFTs found in these categories"})

    return jsonify(
        [n.data() for n in selected_nfts]
    )  # ✅ Send selected NFTs as JSON response


# NL API ENDPOINT (VIEW)
@mintverse.get("/nl/api/nfts/")
def get_nl_nfts():
    categories = ["digital-art", "3d-art", "abstract-art", "comic-art"]

    selected_nfts = []
    for category in categories:
        nft = (
            NFT.query.filter(
                and_(NFT.category == category, NFT.status == NFTStatus.AVAILABLE)
            )
            .offset(3)
            .first()
        )  # ✅ Get 4th item
        if nft:  # Ensure the category has at least one NFT beyond the first 3
            selected_nfts.append(nft)

    # ✅ Handle empty results case
    if not selected_nfts:
        return jsonify({"error": "No NFTs found in these categories"})

    return jsonify(
        [n.data() for n in selected_nfts]
    )  # ✅ Send selected NFTs as JSON response


# EXP SECTION API ENDPOINT
@mintverse.get("/exp/api/nfts/")
def get_exp_section_nfts():
    # ✅ Dynamically get all unique categories stored in the DB
    categories = db.session.query(NFT.category).distinct().all()
    categories = [c[0] for c in categories]  # Convert category tuples to a simple list

    selected_nfts = []
    for category in categories:
        nft = (
            NFT.query.filter(NFT.category == category).offset(3).first()
        )  # ✅ Get 4th item
        if nft:  # Ensure the category has at least four NFTs
            selected_nfts.append(nft)

    # ✅ Handle empty results case
    if not selected_nfts:
        return jsonify(
            {"error": "No NFTs found with at least 6 listed items in each category"}
        )

    return jsonify(
        [n.data() for n in selected_nfts]
    )  # ✅ Send selected NFTs as JSON response


# EXPLORE API ENDPOINT
@mintverse.get("/explore/api/nfts/")
def get_explore_page_nfts():
    nfts = NFT.query.all()
    return jsonify([nft.data() for nft in nfts])


@mintverse.get("/api/nfts/<category>")
def get_nfts_by_category(category):
    # ✅ Preserve category format exactly as stored in the database
    nfts = NFT.query.filter_by(category=category).all()

    # ✅ Handle empty results case
    if not nfts:
        return jsonify({"error": f"No NFTs found in category '{category}'"})

    return jsonify([n.data() for n in nfts])  # ✅ Return NFTs in JSON format


@mintverse.get("/creator/api/nfts/<creator>")
def get_nfts_by_creator(creator):
    try:
        # ✅ Fetch NFTs by creator from the database
        nfts = NFT.query.filter_by(creator=creator).all()

        if not nfts:
            return (
                jsonify({"message": f"No NFTs found for creator - '{creator}'"}),
                404,
            )

        # ✅ Return filtered NFTs in JSON format
        return jsonify([n.data() for n in nfts]), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred fetching NFTs: {str(e)}"}), 500


# BUY PAGE ROUTE (VIEW)
@mintverse.route("/nft/buy/nft_<ref_number>", methods=["GET", "POST"])
@login_required
def buy_page(ref_number):
    try:
        uuid.UUID(ref_number, version=4)  # ✅ Validate reference number format
    except ValueError:
        flash("Invalid NFT reference number format.", "error")
        return redirect(url_for("user.dashboard_page"))

    nft = NFT.query.filter_by(ref_number=ref_number).first()

    if not nft:
        flash("NFT not found.", "error")
        return redirect(url_for("user.dashboard_page"))

    # ✅ Log NFT view (tracking purposes)
    NFTViews.log_view(nft.id, current_user.id)

    ether = Ether.query.filter_by(user_id=current_user.id).first()
    user_balance = ether.main_wallet_balance if ether else 0.0000

    if request.method == "POST":
        # ✅ Check if the current user has already bought this NFT
        if nft.buyer_id == current_user.id:  # ✅ Ensure buyer ID matches user ID
            flash("You have already purchased this NFT.", "info")
            return redirect(
                url_for("mintverse.buy_page", ref_number=ref_number)
            )  # ✅ Redirect to admin.buy_page

        if user_balance < nft.price:
            flash(
                f"Insufficient funds! NFT costs {nft.price} ETH, but you have {user_balance} ETH.",
                "error",
            )
            return redirect(url_for("user.buy_page", ref_number=ref_number))

        return redirect(
            url_for("user.finalising_purchase", ref_number=ref_number)
        )  # ✅ Proceed to finalizing purchase

    return render_template(
        "main/pages/buy-page.html",
        title=f"Buy {nft.nft_name} | MintVerse",
        current_user=current_user,
        nft=nft,
        user_balance=user_balance,
    )


# 3D ART PAGE ROUTE (VIEW)
@mintverse.get("/category/3d-art")
def art3d_page():
    return render_template(
        "main/pages/category/3dart.html",
        title="3D Art | MintVerse",
        current_user=current_user,
    )


# ABSTRACT ART PAGE ROUTE (VIEW)
@mintverse.get("/category/abstract-art")
def abstractart_page():
    return render_template(
        "main/pages/category/abstractart.html",
        title="Abstract Art | MintVerse",
        current_user=current_user,
    )


# CATEGORY ART PAGE ROUTE (VIEW)
@mintverse.get("/category/category-art")
def categoryart_page():
    return render_template(
        "main/pages/category/categoryart.html",
        title="Category Art | MintVerse",
        current_user=current_user,
    )


# DIGITAL ART PAGE ROUTE (VIEW)
@mintverse.get("/category/digital-art")
def digitalart_page():
    return render_template(
        "main/pages/category/digitalart.html",
        title="Digital Art | MintVerse",
        current_user=current_user,
    )


# OUTSIDER ART PAGE ROUTE (VIEW)
@mintverse.get("/category/outsider-art")
def outsiderart_page():
    return render_template(
        "main/pages/category/outsiderart.html",
        title="Outsider Art | MintVerse",
        current_user=current_user,
    )


# FANTASY ART PAGE ROUTE (VIEW)
@mintverse.get("/category/fantasy-art")
def fantasyart_page():
    return render_template(
        "main/pages/category/fantasyart.html",
        title="Fantasy Art | MintVerse",
        current_user=current_user,
    )


# GENERATIVE ART PAGE ROUTE (VIEW)
@mintverse.get("/category/generative-art")
def generativeart_page():
    return render_template(
        "main/pages/category/generativeart.html",
        title="Generative Art | MintVerse",
        current_user=current_user,
    )


# GIF ART PAGE ROUTE (VIEW)
@mintverse.get("/category/gif-art")
def gifart_page():
    return render_template(
        "main/pages/category/gifart.html",
        title="GIF Art | MintVerse",
        current_user=current_user,
    )


# COMIC ART PAGE ROUTE (VIEW)
@mintverse.get("/category/comic-art")
def comicart_page():
    return render_template(
        "main/pages/category/comicart.html",
        title="Comic Art | MintVerse",
        current_user=current_user,
    )


# INSTALLATION ART PAGE ROUTE (VIEW)
@mintverse.get("/category/installation-art")
def installationart_page():
    return render_template(
        "main/pages/category/installationart.html",
        title="Installation Art | MintVerse",
        current_user=current_user,
    )


# POP ART PAGE ROUTE (VIEW)
@mintverse.get("/category/pop-art")
def popart_page():
    return render_template(
        "main/pages/category/popart.html",
        title="Pop Art | MintVerse",
        current_user=current_user,
    )


# DRAWING PAGE ROUTE (VIEW)
@mintverse.get("/category/drawing")
def drawing_page():
    return render_template(
        "main/pages/category/drawing.html",
        title="Drawing | MintVerse",
        current_user=current_user,
    )


# MINIMALISM PAGE ROUTE (VIEW)
@mintverse.get("/category/minimalism")
def minimalism_page():
    return render_template(
        "main/pages/category/minimalism.html",
        title="Minimalism | MintVerse",
        current_user=current_user,
    )


# PAINTING PAGE ROUTE (VIEW)
@mintverse.get("/category/painting")
def painting_page():
    return render_template(
        "main/pages/category/painting.html",
        title="Painting | MintVerse",
        current_user=current_user,
    )


# PHOTOGRAPHY PAGE ROUTE (VIEW)
@mintverse.get("/category/photography")
def photography_page():
    return render_template(
        "main/pages/category/photography.html",
        title="Photography | MintVerse",
        current_user=current_user,
    )


# PHOTOREALISM PAGE ROUTE (VIEW)
@mintverse.get("/category/photorealism")
def photorealism_page():
    return render_template(
        "main/pages/category/photorealism.html",
        title="Photorealism | MintVerse",
        current_user=current_user,
    )


# PRINTMAKING PAGE ROUTE (VIEW)
@mintverse.get("/category/printmaking")
def printmaking_page():
    return render_template(
        "main/pages/category/printmaking.html",
        title="Printmaking | MintVerse",
        current_user=current_user,
    )


# SCULPTURE PAGE ROUTE (VIEW)
@mintverse.get("/category/sculpture")
def sculpture_page():
    return render_template(
        "main/pages/category/sculpture.html",
        title="Sculpture | MintVerse",
        current_user=current_user,
    )


# SURREALISM PAGE ROUTE (VIEW)
@mintverse.get("/category/surrealism")
def surrealism_page():
    return render_template(
        "main/pages/category/surrealism.html",
        title="Surrealism | MintVerse",
        current_user=current_user,
    )


@mintverse.context_processor
def inject_search_form():
    search_form = SearchForm()
    return dict(search_form=search_form)


@mintverse.route("/search", methods=["GET", "POST"])
def search():
    search_form = SearchForm()
    if request.method == "POST":
        if search_form.validate_on_submit():
            searched = search_form.searched.data
            results = (
                NFT.query.filter(
                    or_(
                        NFT.nft_name.like(f"%{searched}%"),
                        NFT.category.like(f"%{searched}%"),
                        NFT.creator.like(f"%{searched}%"),
                        NFT.description.like(f"%{searched}%"),
                    )
                )
                .order_by(NFT.nft_name)
                .all()
            )

            if not results:
                return redirect(
                    url_for("mintverse.search", searched=searched, results=[])
                )

            return render_template(
                "main/pages/search.html",
                searched=searched,
                results=results,
            )

    return render_template(
        "main/pages/search.html",
        search_form=search_form,
        searched=None,
        results=[],
    )
