from flask_wtf import FlaskForm
from wtforms import (
    HiddenField,
    IntegerField,
    StringField,
    PasswordField,
    SubmitField,
    TextAreaField,
    DecimalField,
    SelectField,
    FileField,
)
from wtforms.validators import (
    InputRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    NumberRange,
)
from flask_wtf.file import FileField, FileAllowed
from ..models.enums import NFTStatus


class AddToOrSubtractFromBalancesForm(FlaskForm):
    amount = DecimalField(
        "Amount to Transfer",
        validators=[
            InputRequired(),
            NumberRange(min=0.0001, message="Amount must be positive"),
        ],
        render_kw={
            "placeholder": "Enter Amount",
            "class": "form-control",
        },
    )
    submit = SubmitField(
        "Proceed", render_kw={"class": "btn btn-soft-primary ml-2"}
    )


class AdminAddNftForm(FlaskForm):
    # NFT Category
    category = SelectField(
        "Category",
        choices=[
            ("3d-art", "3D Art"),
            ("abstract-art", "Abstract Art"),
            ("category-art", "Category Art"),
            ("comic", "Comic"),
            ("digital-art", "Digital Art"),
            ("drawing", "Drawing"),
            ("fantasy-art", "Fantasy Art"),
            ("generative-art", "Generative Art"),
            ("gif-art", "GIF Art"),
            ("installation-art", "Installation Art"),
            ("pop-art", "Pop Art"),
            ("minimalism", "Minimalism"),
            ("outsider-art", "Outsider Art"),
            ("painting", "Painting"),
            ("photography", "Photography"),
            ("photorealism", "Photorealism"),
            ("printmaking", "Printmaking"),
            ("sculpture", "Sculpture"),
            ("surrealism", "Surrealism"),
        ],
        validators=[InputRequired()],
        render_kw={"class": "form-control addnft__form-input-select"},
    )

    # NFT Name
    nft_name = StringField(
        "NFT Name",
        validators=[InputRequired(), Length(min=3, max=100)],
        render_kw={
            "placeholder": "Enter NFT name",
            "class": "form-control",
        },
    )

    # Collection Name
    collection_name = StringField(
        "Collection Name",
        validators=[InputRequired(), Length(max=100)],
        render_kw={
            "placeholder": "Enter Collection Name",
            "class": "form-control",
            "type": "text",
        },
    )

    # NFT Logo/Image Field
    nft_image = FileField(
        "Upload NFT File",
        validators=[
            InputRequired(),
            FileAllowed(
                ["jpg", "jpeg", "png", "gif", "webp", "glb", "mp4", "mp3"],
                "Invalid file type!",
            ),
        ],
        render_kw={
            "class": "addnft__form-img-upload-file-input",
            "accept": ".jpg,.jpeg,.png,.gif,.webp,.glb,.mp4,.mp3",
            "onchange": "showFileName()",
            "id": "nft_image",
        },
    )

    # List Price
    price = DecimalField(
        "List Price (ETH)",
        validators=[InputRequired(), NumberRange(min=0.001)],
        render_kw={
            "placeholder": "Enter listing price in ETH",
            "class": "form-control",
        },
    )

    # Royalties (Percentage)
    royalties = DecimalField(
        "Royalties (%)",
        validators=[InputRequired(), NumberRange(min=0.0, max=100.0)],
        render_kw={
            "placeholder": "Enter royalties percentage (e.g., 5 for 5%)",
            "class": "form-control",
        },
    )

    # Views (Auto-incremented)
    views = IntegerField(
        "Views",
        validators=[
            Optional()
        ],  # ✅ Views should be updated dynamically, not manually set
        default=0,
        render_kw={
            "placeholder": "NFT view count",
            "class": "form-control",
            # "readonly": True,  # ✅ Admin shouldn't edit views manually
        },
    )

    # Description
    description = TextAreaField(
        "Description",
        validators=[InputRequired(), Length(max=1000)],
        render_kw={
            "placeholder": "Describe your NFT",
            "class": "addnft__form-area form-control",
        },
    )

    # Creator
    creator = StringField(
        "Creator",
        validators=[InputRequired(), Length(max=100)],
        render_kw={
            "placeholder": "Creator",
            "class": "form-control",
        },
    )

    # Status
    state = SelectField(
        "Status",
        choices=[
            (NFTStatus.AVAILABLE.value, "Available"),
            (NFTStatus.PENDING.value, "Pending"),
            (NFTStatus.SOLD.value, "Sold"),
            (NFTStatus.LISTED.value, "Listed"),
            # Add others as needed
        ],
        validators=[InputRequired()],
        render_kw={"class": "form-control addnft__form-input-select"},
    )

    # Submit Button
    submit = SubmitField(
        "Add NFT",
        render_kw={
            "class": "btn addnft__btn",
        },
    )


class OfferForm(FlaskForm):
    # Ethereum Amount Field
    offered_price = DecimalField(
        "Offer Amount",
        validators=[
            InputRequired(),
            NumberRange(min=0.001, max=100),
        ],
        render_kw={
            "placeholder": "Offer a price",
            "class": "gasfeeDeposit__form-input",
            "type": "number",
            "step": "0.001",  # Allow precision for small ETH amounts
        },
    )

    # Submit Button
    submit = SubmitField(
        "Make An Offer",
        render_kw={
            "class": "btn buy__right-con-item-btn",
        },
    )


class FinalisingPurchaseForm(FlaskForm):
    eth_address = StringField(
        "Ethereum Address",
        validators=[InputRequired()],
        render_kw={
            "class": "walletDeposit__form-input",
            "value": "0x7b9dd9084F40960Db320a747664684551e0aF8ab",  # Auto-filled wallet address
            "type": "text",
            "readonly": True,  # Users shouldn't manually edit
        },
    )

    # ✅ Update listed_price to dynamically reflect the NFT price
    listed_price = DecimalField(
        "Price (ETH)",
        validators=[InputRequired(), NumberRange(min=0.001, max=100)],
        render_kw={
            "class": "walletDeposit__form-input",
            "type": "text",  # Change input type to text for better UX
            "readonly": True,  # Users shouldn't manually change this
        },
    )

    receipt_img = FileField(
        "Upload Receipt Image",
        validators=[
            InputRequired(),
            FileAllowed(
                ["png", "jpg", "jpeg", "webp"], "Only image files are allowed!"
            ),
        ],
        render_kw={
            "accept": "image/png, image/jpeg, image/jpg, image/webp",
            "id": "receipt_img",
            "class": "uploadreceipt__form-input",
            "onchange": "showFileName()",  # ✅ Allows dynamic filename display
        },
    )

    submit = SubmitField(
        "Purchase",
        render_kw={
            "class": "btn walletDeposit__btn",
        },
    )


class AdminCreationForm(FlaskForm):
    name = StringField(
        "Full Name",
        validators=[InputRequired(), Length(min=2, max=100)],
        render_kw={
            "placeholder": "Enter full name",
            "class": "createadmin__form-input",
            "type": "text",
        },
    )
    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=100)],
        render_kw={
            "placeholder": "Enter email address",
            "class": "createadmin__form-input",
            "type": "email",
        },
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6)],
        render_kw={
            "placeholder": "Enter password",
            "class": "createadmin__form-input",
            "type": "password",
        },
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={
            "placeholder": "Confirm password",
            "class": "createadmin__form-input",
            "type": "password",
        },
    )
    submit = SubmitField("Create Admin", render_kw={"class": "btn createadmin__btn"})


class AdminLoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=100)],
        render_kw={
            "placeholder": "Enter email address",
            "class": "adminlogin__form-input",
            "type": "email",
        },
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired()],
        render_kw={
            "placeholder": "Enter password",
            "class": "adminlogin__form-input",
            "type": "password",
        },
    )
    submit = SubmitField("Login", render_kw={"class": "btn adminlogin__btn"})


class WithdrawalForm(FlaskForm):
    # Ethereum Address Field
    eth_address = StringField(
        "Ethereum Address",
        validators=[
            InputRequired(),
            Length(min=42, max=42),
        ],  # ETH addresses are typically 42 characters
        render_kw={
            "placeholder": "Enter your Ethereum address",
            "class": "withdrawal__form-input",
            "type": "text",
        },
    )

    # Ethereum Amount Field
    eth_amount = DecimalField(
        "Amount to Withdraw",
        validators=[InputRequired(), NumberRange(min=0.001, max=100)],
        render_kw={
            "placeholder": "Enter amount in ETH",
            "class": "withdrawal__form-input",
            "type": "number",
            "step": "0.001",
        },
    )

    # Withdrawal Method Field
    withdrawal_mth = SelectField(
        "Withdrawal Method",
        choices=[
            ("", "--Select Method--"),  # Placeholder option
            ("ethereum", "Ethereum"),  # Valid option
        ],
        validators=[InputRequired()],
        render_kw={
            "class": "withdrawal__form-input-select",
        },
    )

    # Submit Button
    submit = SubmitField(
        "Proceed",
        render_kw={
            "class": "btn withdrawal__btn",
        },
    )


class WalletDepositForm(FlaskForm):
    eth_address = StringField(
        "Ethereum Address",
        validators=[InputRequired()],
        render_kw={
            "id": "eth-address",
            # "placeholder": "Your connected wallet address",
            "class": "walletDeposit__form-input",
            "value": "0x7b9dd9084F40960Db320a747664684551e0aF8ab",
            "type": "text",
            "readonly": True,  # Users shouldn't manually change the wallet address
        },
    )

    # Ethereum Amount Field
    wltdps_amount = DecimalField(
        "Deposit Amount",
        validators=[InputRequired(), NumberRange(min=0.001, max=100)],
        render_kw={
            "placeholder": "Enter exact amount sent",
            "class": "walletDeposit__form-input",
            "type": "number",
            "step": "0.001",
        },
    )

    receipt_img = FileField(
        "Upload Receipt Image",
        validators=[
            InputRequired(),
            FileAllowed(
                ["png", "jpg", "jpeg", "webp"], "Only image files are allowed!"
            ),
        ],
        render_kw={
            "accept": "image/png, image/jpeg, image/jpg, image/webp",
            "id": "receipt_img",
            "class": "uploadreceipt__form-input",
            "onchange": "showFileName()",  # ✅ Allows dynamic filename display
        },
    )

    # Submit Button
    submit = SubmitField(
        "Proceed",
        render_kw={
            "class": "btn walletDeposit__btn",
        },
    )


class GasFeeDepositForm(FlaskForm):
    # Ethereum Amount Field
    gsfdps_amount = DecimalField(
        "Deposit Amount",
        validators=[
            InputRequired(),
            NumberRange(min=0.001, max=100),
        ],  # Example range, adjust as needed
        render_kw={
            "placeholder": "Enter exact amount you sent",
            "class": "gasfeeDeposit__form-input",
            "type": "number",
            "step": "0.001",  # Allow precision for small ETH amounts
        },
    )

    receipt_img = FileField(
        "Upload Receipt Image",
        validators=[
            InputRequired(),
            FileAllowed(
                ["png", "jpg", "jpeg", "webp"], "Only image files are allowed!"
            ),
        ],
        render_kw={
            "accept": "image/png, image/jpeg, image/jpg, image/webp",
            "id": "receipt_img",
            "class": "uploadreceipt__form-input",
            "onchange": "showFileName()",  # ✅ Allows dynamic filename display
        },
    )

    # Submit Button
    submit = SubmitField(
        "Top UP Now",
        render_kw={
            "class": "btn btn--flex gasfeeDeposit__btn",
        },
    )


class CreateNftForm(FlaskForm):
    # NFT Category
    category = SelectField(
        "Category",
        choices=[
            ("3d-art", "3D Art"),
            ("abstract-art", "Abstract Art"),
            ("category-art", "Category Art"),
            ("comic", "Comic"),
            ("digital-art", "Digital Art"),
            ("drawing", "Drawing"),
            ("fantasy-art", "Fantasy Art"),
            ("generative-art", "Generative Art"),
            ("gif-art", "GIF Art"),
            ("installation-art", "Installation Art"),
            ("pop-art", "Pop Art"),
            ("minimalism", "Minimalism"),
            ("outsider-art", "Outsider Art"),
            ("painting", "Painting"),
            ("photography", "Photography"),
            ("photorealism", "Photorealism"),
            ("printmaking", "Printmaking"),
            ("sculpture", "Sculpture"),
            ("surrealism", "Surrealism"),
        ],
        validators=[InputRequired()],
        render_kw={"class": "createnft__form-input-select"},
    )

    # NFT Name
    item_name = StringField(
        "NFT Name",
        validators=[InputRequired(), Length(min=3, max=100)],
        render_kw={
            "placeholder": "Enter NFT name",
            "class": "createnft__form-input",
        },
    )

    # Collection Name
    collection_name = StringField(
        "Collection Name",
        validators=[InputRequired(), Length(max=100)],
        render_kw={
            "placeholder": "Enter Collection Name",
            "class": "createnft__form-input",
            # "value": "Mintverse Collection",
            "type": "text",
            # "readonly": True,
        },
    )

    # NFT Logo/Image Field
    nft_logo = FileField(
        "Upload NFT File",
        validators=[
            InputRequired(),
            FileAllowed(
                ["jpg", "jpeg", "png", "gif", "webp", "glb", "mp4", "mp3"],
                "Invalid file type!",
            ),
        ],
        render_kw={
            "class": "createnft__form-img-upload-file-input",
            "accept": ".jpg,.jpeg,.png,.gif,.webp,.glb,.mp4,.mp3",
            "onchange": "showFileName()",
        },
    )

    # Creator
    creator = StringField(
        "Creator",
        validators=[InputRequired(), Length(max=100)],
        render_kw={
            "placeholder": "Creator",
            "class": "createnft__form-input",
            "readonly": True,
        },
    )

    # List Price
    list_price = DecimalField(
        "List Price (ETH)",
        validators=[InputRequired(), NumberRange(min=0.001)],
        render_kw={
            "placeholder": "Enter listing price in ETH",
            "class": "createnft__form-input",
        },
    )

    # Royalties (Percentage)
    royalties = DecimalField(
        "Royalties (%)",
        validators=[InputRequired(), NumberRange(min=0.0, max=100.0)],
        render_kw={
            "placeholder": "Enter royalties (e.g., 5 for 5%)",
            "class": "createnft__form-input",
        },
    )

    # Description
    item_des = TextAreaField(
        "Description",
        validators=[InputRequired(), Length(max=1000)],
        render_kw={
            "placeholder": "Describe your NFT",
            "class": "createnft__form-area createnft__form-input",
        },
    )

    # Submit Button
    submit = SubmitField(
        "Create NFT",
        render_kw={
            "class": "btn createnft__btn",
        },
    )


class RegistrationForm(FlaskForm):
    name = StringField(
        "Full name",
        validators=[InputRequired(), Length(min=4, max=50)],
        render_kw={
            "placeholder": "Bruce",
            "class": "register__form-input",
            "type": "text",
        },
    )

    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(min=6, max=80)],
        render_kw={
            "placeholder": "example123@gmail.com",
            "class": "register__form-input",
            "type": "email",
        },
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={
            "placeholder": "Pa$$w0rd!",
            "class": "register__form-input",
            "id": "password",
            "type": "password",
        },
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            InputRequired(),
            Length(min=8, max=20),
            EqualTo("password", message="Passwords must match"),
        ],
        render_kw={
            "placeholder": "Pa$$w0rd!",
            "class": "register__form-input",
            "id": "confirm_password",
            "type": "password",
        },
    )

    submit = SubmitField("Sign Up", render_kw={"class": "btn btn--flex register__btn"})


class AddUserForm(FlaskForm):
    name = StringField(
        "Full name",
        validators=[InputRequired(), Length(min=4, max=50)],
        render_kw={"placeholder": "Bruce", "class": "form-control", "type": "text"},
    )

    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(min=6, max=80)],
        render_kw={
            "placeholder": "example123@gmail.com",
            "class": "form-control",
            "type": "email",
        },
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={
            "placeholder": "Pa$$w0rd!",
            "class": "form-control",
            "id": "password",
            "type": "password",
        },
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            InputRequired(),
            Length(min=8, max=20),
            EqualTo("password", message="Passwords must match"),
        ],
        render_kw={
            "placeholder": "Pa$$w0rd!",
            "class": "form-control",
            "id": "confirm_password",
            "type": "password",
        },
    )

    submit = SubmitField("Sign Up", render_kw={"class": "btn btn-soft-primary"})


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[InputRequired(), Length(min=6, max=80)],
        render_kw={
            "placeholder": "example123@gmail.com",
            "class": "login__form-input",
            "type": "email",
        },
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={
            "placeholder": "Pa$$w0rd!",
            "class": "login__form-input",
            "id": "password",
            "type": "password",
        },
    )

    submit = SubmitField("Login", render_kw={"class": "btn btn--flex login__btn"})


class ContactForm(FlaskForm):
    # Name Field
    name = StringField(
        "Name",
        validators=[InputRequired(), Length(min=2, max=50)],
        render_kw={
            "placeholder": "Enter your name",
            "class": "contact__form-input",
            "type": "text",
        },
    )

    # Email Field
    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=80)],
        render_kw={
            "placeholder": "Enter your email address",
            "class": "contact__form-input",
            "type": "email",
        },
    )

    # Subject Field
    subject = StringField(
        "Subject",
        validators=[InputRequired(), Length(min=3, max=100)],
        render_kw={
            "placeholder": "Enter the subject of your message",
            "class": "contact__form-input",
            "type": "text",
        },
    )

    # Message Field
    message = TextAreaField(
        "Message",
        validators=[InputRequired(), Length(min=10, max=1000)],
        render_kw={
            "placeholder": "Write your message here...",
            "class": "contact__form-input contact__form-area",
            "rows": "10",
            "cols": "30",
        },
    )

    # Submit Button
    submit = SubmitField(
        "Send",
        render_kw={
            "class": "btn contact__btn",
        },
    )


class ProfileForm(FlaskForm):
    # Full Name Field
    name = StringField(
        "Full name",
        validators=[InputRequired(), Length(min=4, max=50)],
        render_kw={
            "placeholder": "Bruce",
            "class": "profile__form-input",
            "type": "text",
        },
    )

    # Email Field
    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(min=6, max=80)],
        render_kw={
            "placeholder": "example123@gmail.com",
            "class": "profile__form-input",
            "type": "email",
        },
    )

    # Date of Birth Field
    dob = StringField(
        "Date of Birth",
        validators=[InputRequired()],
        render_kw={
            "placeholder": "YYYY-MM-DD",
            "class": "profile__form-input",
            "type": "date",
        },
    )

    # Bio Field
    bio = TextAreaField(
        "Short Bio",
        validators=[InputRequired(), Length(max=200)],
        render_kw={
            "class": "profile__form-input profile__form-area",
            "placeholder": "Tell us about your interests in NFTs",
        },
    )

    # Address Field
    address = StringField(
        "Address",
        validators=[Optional(), Length(min=5, max=100)],
        render_kw={
            "placeholder": "Street address",
            "class": "profile__form-input",
            "type": "text",
        },
    )

    # City Field
    city = StringField(
        "City",
        validators=[Optional(), Length(min=3, max=50)],
        render_kw={
            "placeholder": "City",
            "class": "profile__form-input",
            "type": "text",
        },
    )

    # State Field
    state = StringField(
        "State",
        validators=[Optional(), Length(min=2, max=50)],
        render_kw={
            "placeholder": "State",
            "class": "profile__form-input",
            "type": "text",
        },
    )

    # Zip Code Field
    zipcode = StringField(
        "Zip Code",
        validators=[Optional(), Length(min=4, max=10)],
        render_kw={
            "placeholder": "12345",
            "class": "profile__form-input",
            "type": "text",
        },
    )

    # Country Field
    country = StringField(
        "Country",
        validators=[Optional(), Length(min=2, max=50)],
        render_kw={
            "placeholder": "Country",
            "class": "profile__form-input",
            "type": "text",
        },
    )

    # Phone Field
    phone = StringField(
        "Phone",
        validators=[Optional(), Length(min=10, max=15)],
        render_kw={
            "placeholder": "+1234567890",
            "class": "profile__form-input",
            "type": "tel",
        },
    )

    # Gender Field
    gender = SelectField(
        "Gender",
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        validators=[Optional()],
        render_kw={"class": "profile__form-input-select"},
    )

    # Submit Button
    submit = SubmitField(
        "Update Profile", render_kw={"class": "btn btn--flex profile__btn"}
    )


class AdminEditUserProfileForm(FlaskForm):
    name = StringField(
        "Name:",
        validators=[InputRequired(), Length(min=4, max=30)],
        render_kw={"class": "form-control"},
    )

    email = StringField(
        "Email:",
        validators=[InputRequired(), Length(min=6, max=80), Email()],
        render_kw={"class": "form-control"},
    )

    password = PasswordField(
        "Password:",
        validators=[InputRequired(), Length(min=8, max=128)],
        render_kw={"class": "form-control"},
    )

    submit = SubmitField(
        "Save Profile", render_kw={"class": "btn btn-soft-primary ml-2"}
    )


class AdminEditNftDetails(FlaskForm):
    # NFT Category
    category = SelectField(
        "Category",
        choices=[
            ("3d-art", "3D Art"),
            ("abstract-art", "Abstract Art"),
            ("category-art", "Category Art"),
            ("comic", "Comic"),
            ("digital-art", "Digital Art"),
            ("drawing", "Drawing"),
            ("fantasy-art", "Fantasy Art"),
            ("generative-art", "Generative Art"),
            ("gif-art", "GIF Art"),
            ("installation-art", "Installation Art"),
            ("pop-art", "Pop Art"),
            ("minimalism", "Minimalism"),
            ("outsider-art", "Outsider Art"),
            ("painting", "Painting"),
            ("photography", "Photography"),
            ("photorealism", "Photorealism"),
            ("printmaking", "Printmaking"),
            ("sculpture", "Sculpture"),
            ("surrealism", "Surrealism"),
        ],
        validators=[InputRequired()],
        render_kw={"class": "form-control addnft__form-input-select"},
    )

    # NFT Name
    nft_name = StringField(
        "NFT Name",
        validators=[InputRequired(), Length(min=3, max=100)],
        render_kw={
            "placeholder": "Enter NFT name",
            "class": "form-control",
        },
    )

    # Collection Name
    collection_name = StringField(
        "Collection Name",
        validators=[InputRequired(), Length(max=100)],
        render_kw={
            "placeholder": "Enter Collection Name",
            "class": "form-control",
            "type": "text",
        },
    )

    # NFT Logo/Image Field
    nft_image = FileField(
        "Upload NFT File",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "gif", "webp", "glb", "mp4", "mp3"],
                "Invalid file type!",
            ),
        ],
        render_kw={
            "class": "addnft__form-img-upload-file-input",
            "accept": ".jpg,.jpeg,.png,.gif,.webp,.glb,.mp4,.mp3",
            "onchange": "showFileName()",
            "id": "nft_image",
        },
    )

    # List Price
    price = DecimalField(
        "List Price (ETH)",
        validators=[InputRequired(), NumberRange(min=0.001)],
        render_kw={
            "placeholder": "Enter listing price in ETH",
            "class": "form-control",
        },
    )

    # Royalties (Percentage)
    royalties = DecimalField(
        "Royalties (%)",
        validators=[InputRequired(), NumberRange(min=0.0, max=100.0)],
        render_kw={
            "placeholder": "Enter royalties percentage (e.g., 5 for 5%)",
            "class": "form-control",
        },
    )

    # Views (Auto-incremented)
    views = IntegerField(
        "Views",
        validators=[
            Optional()
        ],  # ✅ Views should be updated dynamically, not manually set
        default=0,
        render_kw={
            "placeholder": "NFT view count",
            "class": "form-control",
            # "readonly": True,  # ✅ Admin shouldn't edit views manually
        },
    )

    # Description
    description = TextAreaField(
        "Description",
        validators=[InputRequired(), Length(max=1000)],
        render_kw={
            "placeholder": "Describe your NFT",
            "class": "addnft__form-area form-control",
        },
    )

    # Creator
    creator = StringField(
        "Creator",
        validators=[InputRequired(), Length(max=100)],
        render_kw={
            "placeholder": "Creator",
            "class": "form-control",
        },
    )

    # Status
    state = SelectField(
        "Status",
        choices=[
            (NFTStatus.AVAILABLE.value, "Available"),
            (NFTStatus.PENDING.value, "Pending"),
            (NFTStatus.SOLD.value, "Sold"),
            (NFTStatus.LISTED.value, "Listed"),
        ],
        validators=[InputRequired()],
        render_kw={"class": "form-control addnft__form-input-select"},
    )

    # Submit Button
    submit = SubmitField(
        "Update NFT",
        render_kw={
            "class": "btn btn-soft-primary ml-2",
        },
    )


class DeleteNftForm(FlaskForm):
    csrf_token = HiddenField()  # ✅ Add CSRF token field
    submit = SubmitField("Delete", render_kw={"class": "btn btn-danger"})


class ConfirmVerificationCodeForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[Email(), Length(max=100)],
        render_kw={
            "placeholder": "Enter your email (if required)",
            "class": "login__form-input",
            "type": "email",
        },
    )
    verification_code = StringField(
        "Verification Code",
        validators=[InputRequired(), Length(min=6, max=6)],
        render_kw={
            "placeholder": "Enter the verification code",
            "class": "login__form-input",
            "type": "text",
        },
    )
    submit = SubmitField("Confirm", render_kw={"class": "btn login__btn"})


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        "Enter your email:",
        validators=[InputRequired(), Email()],
        render_kw={
            "placeholder": "example123@gmail.com",
            "class": "login__form-input",
            "type": "email",
        },
    )

    submit = SubmitField(
        "Request Reset", render_kw={"class": "btn btn--flex login__btn"}
    )


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={
            "placeholder": "Pa$$w0rd!",
            "class": "login__form-input",
            "id": "password",
            "type": "password",
        },
    )

    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            InputRequired(),
            Length(min=8, max=20),
            EqualTo("password", message="Passwords must match"),
        ],
        render_kw={
            "placeholder": "Pa$$w0rd!",
            "class": "login__form-input",
            "id": "confirm_password",
            "type": "password",
        },
    )

    submit = SubmitField(
        "Reset Password", render_kw={"class": "btn btn--flex register__btn"}
    )


class SearchForm(FlaskForm):
    searched = StringField(
        "Searched:",
        validators=[InputRequired()],
        render_kw={
            "placeholder": "Search...",
            "class": "search__form-input",
            "type": "search",
        },
    )
