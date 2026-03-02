import asyncio

from playwright.async_api import Page, async_playwright

from app.services.extract import G28Data, PassportData

FORM_URL = "https://mendrika-alma.github.io/form-submission/"


async def _fill_field(page: Page, selector: str, value: str) -> None:
    """Fill a text/tel/email/date input if value is non-empty."""
    if value:
        await page.fill(selector, value)
        await asyncio.sleep(0.1)


async def _select_field(page: Page, selector: str, value: str) -> None:
    """Select a dropdown option if value is non-empty."""
    if value:
        await page.select_option(selector, value)
        await asyncio.sleep(0.1)


async def _fill_g28(page: Page, g28: G28Data) -> None:
    """Fill Part 1 (Attorney Info) and Part 2 (Eligibility) from G28 data."""
    # Part 1 - Attorney info
    await _fill_field(page, "#family-name", g28.family_name)
    await _fill_field(page, "#given-name", g28.given_name)
    await _fill_field(page, "#middle-name", g28.middle_name)

    # Address
    await _fill_field(page, "#street-number", g28.street_number_and_name)

    # Apt/Ste/Flr checkbox + number
    if g28.apt_ste_flr:
        apt_lower = g28.apt_ste_flr.lower().strip()
        if "ste" in apt_lower:
            await page.check("#ste")
        elif "flr" in apt_lower or "floor" in apt_lower:
            await page.check("#flr")
        else:
            await page.check("#apt")
        # Extract just the number part if the value contains a prefix
        number = g28.apt_ste_flr.strip()
        for prefix in ("apt.", "apt", "ste.", "ste", "flr.", "flr", "floor", "#"):
            if number.lower().startswith(prefix):
                number = number[len(prefix):].strip()
                break
        if number:
            await _fill_field(page, "#apt-number", number)

    await _fill_field(page, "#city", g28.city)
    await _select_field(page, "#state", g28.state)
    await _fill_field(page, "#zip", g28.zip_code)
    await _fill_field(page, "#country", g28.country)

    # Contact
    await _fill_field(page, "#daytime-phone", g28.daytime_phone)
    await _fill_field(page, "#mobile-phone", g28.mobile_phone)
    await _fill_field(page, "#email", g28.email)

    # Part 2 - Eligibility
    await _fill_field(page, "#licensing-authority", g28.licensing_authority)
    await _fill_field(page, "#bar-number", g28.bar_number)
    await _fill_field(page, "#law-firm", g28.law_firm_name)


async def _fill_passport(page: Page, passport: PassportData) -> None:
    """Fill Part 3 (Passport Info) from passport data."""
    await _fill_field(page, "#passport-surname", passport.last_name)
    # Note: the form HTML reuses id="passport-given-names" for both first name
    # and middle name fields. Use nth-match to target them separately.
    await _fill_field(
        page, "#passport-given-names >> nth=0", passport.first_name
    )
    await _fill_field(
        page, "#passport-given-names >> nth=1", passport.middle_name
    )

    await _fill_field(page, "#passport-number", passport.passport_number)
    await _fill_field(page, "#passport-country", passport.country_of_issue)
    await _fill_field(page, "#passport-nationality", passport.nationality)

    # Date fields expect YYYY-MM-DD format
    await _fill_field(page, "#passport-dob", passport.date_of_birth)
    await _fill_field(page, "#passport-pob", passport.place_of_birth)

    # Sex dropdown: M, F, or X
    sex_val = passport.sex.strip().upper()[:1] if passport.sex else ""
    await _select_field(page, "#passport-sex", sex_val)

    await _fill_field(page, "#passport-issue-date", passport.date_of_issue)
    await _fill_field(page, "#passport-expiry-date", passport.date_of_expiration)


async def fill_form(
    passport_data: PassportData, g28_data: G28Data
) -> bytes:
    """Open a visible browser, fill the form live, return a screenshot. Browser stays open."""
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False)
    page = await browser.new_page(viewport={"width": 1280, "height": 900})
    await page.goto(FORM_URL, wait_until="networkidle")

    await _fill_g28(page, g28_data)
    await _fill_passport(page, passport_data)

    await asyncio.sleep(0.3)
    return await page.screenshot(full_page=True)
