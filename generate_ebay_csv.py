"""
Generate eBay File Exchange CSV from card data.
Uses the EXACT template format downloaded from eBay Seller Hub.
"""
import csv
import os

# eBay template header (from the downloaded template, minus ImmediatePayRequired)
HEADER_ROW_0 = "Info,Version=1.0.0,Template=fx_category_template_EBAY_US"

HEADERS = [
    "*Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)",
    "CustomLabel", "*Category", "StoreCategory", "*Title", "Subtitle",
    "Relationship", "RelationshipDetails", "ScheduleTime",
    "*ConditionID",
    "CD:Professional Grader - (ID: 27501)",
    "CD:Grade - (ID: 27502)",
    "CDA:Certification Number - (ID: 27503)",
    "CD:Card Condition - (ID: 40001)",
    "*C:Sport", "C:Player/Athlete", "C:Season", "C:Year Manufactured",
    "C:Manufacturer", "C:Signed By", "C:Parallel/Variety", "C:Features",
    "C:Set", "C:Team", "C:League", "C:Autographed", "C:Card Name",
    "C:Card Number", "C:Type", "C:Autograph Authentication", "C:Grade",
    "C:Card Size", "C:Country of Origin", "C:Graded", "C:Professional Grader",
    "C:Material", "C:Autograph Format", "C:Vintage", "C:Card Condition",
    "C:Event/Tournament", "C:Language", "C:Original/Licensed Reprint",
    "C:Certification Number", "C:Autograph Authentication Number",
    "C:California Prop 65 Warning", "C:Card Thickness", "C:Customized",
    "C:Insert Set", "C:Print Run", "C:Officially Licensed",
    "C:Unit Quantity", "C:Unit Type", "C:Number of Cards",
    "C:Sticker Number", "C:Collection", "C:Sticker Subject",
    "C:Sticker Condition", "C:Finish", "C:Sticker Length",
    "C:Sticker State", "C:Sticker Width", "C:Title",
    "PicURL", "GalleryType", "VideoID",
    "*Description", "*Format", "*Duration", "*StartPrice",
    "BuyItNowPrice", "BestOfferEnabled", "BestOfferAutoAcceptPrice",
    "MinimumBestOfferPrice", "*Quantity",
    "*Location", "ShippingType",
    "ShippingService-1:Option", "ShippingService-1:Cost",
    "ShippingService-2:Option", "ShippingService-2:Cost",
    "*DispatchTimeMax", "PromotionalShippingDiscount",
    "ShippingDiscountProfileID",
    "*ReturnsAcceptedOption", "ReturnsWithinOption",
    "RefundOption", "ShippingCostPaidByOption",
    "AdditionalDetails",
    "Product Safety Pictograms", "Product Safety Statements",
    "Product Safety Component", "Regulatory Document Ids",
    "Manufacturer Name", "Manufacturer AddressLine1",
    "Manufacturer AddressLine2", "Manufacturer City",
    "Manufacturer Country", "Manufacturer PostalCode",
    "Manufacturer StateOrProvince", "Manufacturer Phone",
    "Manufacturer Email", "Manufacturer ContactURL",
    "Responsible Person 1", "Responsible Person 1 Type",
    "Responsible Person 1 AddressLine1",
    "Responsible Person 1 AddressLine2",
    "Responsible Person 1 City", "Responsible Person 1 Country",
    "Responsible Person 1 PostalCode",
    "Responsible Person 1 StateOrProvince",
    "Responsible Person 1 Phone", "Responsible Person 1 Email",
    "Responsible Person 1 ContactURL",
]


def make_row(
    custom_label, title, description, price,
    sport, player, season, year, manufacturer,
    parallel_variety="Base", features="", card_set="",
    team="", league="", card_name="", card_number="",
    card_type="Base", graded="No", vintage="Yes",
    card_condition="Near Mint or Better",
    country="United States", insert_set="",
    num_cards="1", condition_id="4000",
    best_offer=False,
):
    """Build a single data row dict matching HEADERS."""
    row = {h: "" for h in HEADERS}

    row["*Action(SiteID=US|Country=US|Currency=USD|Version=1193|CC=UTF-8)"] = "Add"
    row["CustomLabel"] = custom_label
    row["*Category"] = "261328"
    row["*Title"] = title[:80]
    row["*ConditionID"] = str(condition_id)
    row["CD:Card Condition - (ID: 40001)"] = card_condition
    row["*C:Sport"] = sport
    row["C:Player/Athlete"] = player
    row["C:Season"] = str(season)
    row["C:Year Manufactured"] = str(year)
    row["C:Manufacturer"] = manufacturer
    row["C:Parallel/Variety"] = parallel_variety
    row["C:Features"] = features
    row["C:Set"] = card_set
    row["C:Team"] = team
    row["C:League"] = league
    row["C:Autographed"] = "No"
    row["C:Card Name"] = card_name
    row["C:Card Number"] = str(card_number) if card_number else ""
    row["C:Type"] = card_type
    row["C:Country of Origin"] = country
    row["C:Graded"] = graded
    row["C:Vintage"] = vintage
    row["C:Card Condition"] = card_condition
    row["C:Original/Licensed Reprint"] = "Original"
    row["C:Number of Cards"] = str(num_cards)
    row["C:Insert Set"] = insert_set

    row["*Description"] = description
    row["*Format"] = "FixedPrice"
    row["*Duration"] = "GTC"
    row["*StartPrice"] = str(price)
    if best_offer:
        row["BestOfferEnabled"] = "1"
    row["*Quantity"] = "1"
    row["ShippingType"] = "Flat"
    row["ShippingService-1:Option"] = "USPSMedia"
    row["ShippingService-1:Cost"] = "0"
    row["*DispatchTimeMax"] = "3"
    row["*ReturnsAcceptedOption"] = "ReturnsAccepted"
    row["ReturnsWithinOption"] = "Days_30"
    row["RefundOption"] = "MoneyBack"
    row["ShippingCostPaidByOption"] = "Buyer"

    return row


def write_csv(rows, output_path):
    """Write rows to eBay File Exchange CSV."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        # Line 1: Info row
        f.write(HEADER_ROW_0 + "\n")
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Wrote {len(rows)} listings to {output_path}")


# =============================================
# BO JACKSON LOT
# =============================================
def bo_jackson_lot():
    rows = []

    # LOT listing
    rows.append(make_row(
        custom_label="BOJACK-LOT",
        title="Bo Jackson 15 Card Lot Football Baseball Topps Donruss Fleer 1989-2021",
        description=(
            "Bo Jackson 15-card lot spanning football and baseball. "
            "6 football cards (1989-2021) and 9 baseball cards (1990-1991). "
            "Highlights: 1989 Topps #110 Bo Knows Yardage, "
            "2020-21 Donruss Retro Series insert, "
            "1990 Donruss MVP #BC-4. "
            "Also includes 1991 Score, 1990 Fleer, 1990 Pro Set, "
            "1990 Topps, 1990 Donruss base and variations, "
            "and 1990 Fleer Human Dynamos insert w/ Kirby Puckett. "
            "All cards ungraded raw. Ships securely in top loader and rigid mailer."
        ),
        price="19.99",
        sport="Football", player="Bo Jackson", season="1989", year="1989",
        manufacturer="Topps", card_set="Topps", team="Los Angeles Raiders",
        league="NFL", card_name="Bo Jackson", card_type="Lot",
        num_cards="15", best_offer=True,
    ))

    # 1. 1989 Topps #110 Bo Knows Yardage
    rows.append(make_row(
        custom_label="BOJACK-01",
        title="1989 Topps #110 Bo Jackson Bo Knows Yardage Raiders Football",
        description="1989 Topps #110 Bo Jackson Bo Knows Yardage - Los Angeles Raiders. Iconic card from the Bo Knows era. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="4.99", sport="Football", player="Bo Jackson",
        season="1989", year="1989", manufacturer="Topps",
        card_set="Topps", team="Los Angeles Raiders", league="NFL",
        card_name="Bo Knows Yardage", card_number="110",
    ))

    # 2. 1991 Score #300
    rows.append(make_row(
        custom_label="BOJACK-02",
        title="1991 Score #300 Bo Jackson Los Angeles Raiders Football Card",
        description="1991 Score #300 Bo Jackson - Los Angeles Raiders. Black Raiders uniform. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="1.99", sport="Football", player="Bo Jackson",
        season="1991", year="1991", manufacturer="Score",
        card_set="Score", team="Los Angeles Raiders", league="NFL",
        card_name="Bo Jackson", card_number="300",
    ))

    # 3. 1990 Fleer #285
    rows.append(make_row(
        custom_label="BOJACK-03",
        title="1990 Fleer #285 Bo Jackson Los Angeles Raiders Football Card",
        description="1990 Fleer #285 Bo Jackson - Los Angeles Raiders. White border design. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="1.99", sport="Football", player="Bo Jackson",
        season="1990", year="1990", manufacturer="Fleer",
        card_set="Fleer", team="Los Angeles Raiders", league="NFL",
        card_name="Bo Jackson", card_number="285",
    ))

    # 4. 1990 Pro Set #297
    rows.append(make_row(
        custom_label="BOJACK-04",
        title="1990 Pro Set #297 Bo Jackson Los Angeles Raiders Football Card",
        description="1990 Pro Set #297 Bo Jackson - Los Angeles Raiders. Multi-player action shot. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="1.99", sport="Football", player="Bo Jackson",
        season="1990", year="1990", manufacturer="Pro Set",
        card_set="Pro Set", team="Los Angeles Raiders", league="NFL",
        card_name="Bo Jackson", card_number="297",
    ))

    # 5. 2020-21 Donruss Retro Series
    rows.append(make_row(
        custom_label="BOJACK-05",
        title="2020 Donruss Retro Series Bo Jackson Insert Raiders Football",
        description="2020-21 Donruss Retro Series Bo Jackson insert - Los Angeles Raiders. Purple/black cosmic background. Modern insert card. Ships in top loader and rigid mailer.",
        price="2.99", sport="Football", player="Bo Jackson",
        season="2020", year="2020", manufacturer="Donruss",
        parallel_variety="Retro Series", features="Insert",
        card_set="Donruss", team="Los Angeles Raiders", league="NFL",
        card_name="Bo Jackson", card_type="Insert",
        insert_set="Retro Series", vintage="No",
    ))

    # 6. 1991 Score #300 (duplicate)
    rows.append(make_row(
        custom_label="BOJACK-06",
        title="1991 Score #300 Bo Jackson Raiders Football Card",
        description="1991 Score #300 Bo Jackson - Los Angeles Raiders. Second copy. Black Raiders uniform. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="1.99", sport="Football", player="Bo Jackson",
        season="1991", year="1991", manufacturer="Score",
        card_set="Score", team="Los Angeles Raiders", league="NFL",
        card_name="Bo Jackson", card_number="300",
    ))

    # 7. 1990 Donruss #61 Red Border
    rows.append(make_row(
        custom_label="BOJACK-07",
        title="1990 Donruss #61 Bo Jackson Kansas City Royals Baseball Card",
        description="1990 Donruss #61 Bo Jackson - Kansas City Royals. Red border. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="1.49", sport="Baseball", player="Bo Jackson",
        season="1990", year="1990", manufacturer="Donruss",
        card_set="Donruss", team="Kansas City Royals", league="MLB",
        card_name="Bo Jackson", card_number="61",
    ))

    # 8. 1990 Donruss #61 Blue Border
    rows.append(make_row(
        custom_label="BOJACK-08",
        title="1990 Donruss #61 Bo Jackson Royals Blue Border Variation",
        description="1990 Donruss #61 Bo Jackson - Kansas City Royals. Blue border color variation. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="1.49", sport="Baseball", player="Bo Jackson",
        season="1990", year="1990", manufacturer="Donruss",
        card_set="Donruss", team="Kansas City Royals", league="MLB",
        card_name="Bo Jackson", card_number="61",
    ))

    # 9. 1990 Donruss MVP BC-4
    rows.append(make_row(
        custom_label="BOJACK-09",
        title="1990 Donruss MVP BC-4 Bo Jackson Royals Baseball Insert Card",
        description="1990 Donruss MVP #BC-4 Bo Jackson - Kansas City Royals. Orange MVP background insert card. Ships in top loader and rigid mailer.",
        price="2.99", sport="Baseball", player="Bo Jackson",
        season="1990", year="1990", manufacturer="Donruss",
        parallel_variety="MVP", features="Insert",
        card_set="Donruss", team="Kansas City Royals", league="MLB",
        card_name="Bo Jackson", card_number="BC-4", card_type="Insert",
        insert_set="MVP",
    ))

    # 10. 1991 Donruss #35
    rows.append(make_row(
        custom_label="BOJACK-10",
        title="1991 Donruss #35 Bo Jackson Kansas City Royals Baseball Card",
        description="1991 Donruss #35 Bo Jackson - Kansas City Royals. Green/teal border design. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="1.49", sport="Baseball", player="Bo Jackson",
        season="1991", year="1991", manufacturer="Donruss",
        card_set="Donruss", team="Kansas City Royals", league="MLB",
        card_name="Bo Jackson", card_number="35",
    ))

    # 11. 1990 Fleer Human Dynamos
    rows.append(make_row(
        custom_label="BOJACK-11",
        title="1990 Fleer Human Dynamos Insert Kirby Puckett Bo Jackson",
        description="1990 Fleer Human Dynamos insert featuring Kirby Puckett and Bo Jackson. Dual player insert card. Ships in top loader and rigid mailer.",
        price="2.99", sport="Baseball", player="Bo Jackson",
        season="1990", year="1990", manufacturer="Fleer",
        parallel_variety="Human Dynamos", features="Insert",
        card_set="Fleer", team="Kansas City Royals", league="MLB",
        card_name="Human Dynamos", card_type="Insert",
        insert_set="Human Dynamos",
    ))

    # 12. 1990 Donruss Triple Play #91
    rows.append(make_row(
        custom_label="BOJACK-12",
        title="1990 Donruss Triple Play #91 Bo Jackson White Sox Baseball",
        description="1990 Donruss Triple Play #91 Bo Jackson - Chicago White Sox. Smiling portrait. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="1.49", sport="Baseball", player="Bo Jackson",
        season="1990", year="1990", manufacturer="Donruss",
        card_set="Donruss", team="Chicago White Sox", league="MLB",
        card_name="Bo Jackson", card_number="91",
    ))

    # 13. 1990 Topps #300
    rows.append(make_row(
        custom_label="BOJACK-13",
        title="1990 Topps #300 Bo Jackson Kansas City Royals Baseball Card",
        description="1990 Topps #300 Bo Jackson - Kansas City Royals. Classic yellow border Topps base card. Ships in top loader and rigid mailer.",
        price="1.99", sport="Baseball", player="Bo Jackson",
        season="1990", year="1990", manufacturer="Topps",
        card_set="Topps", team="Kansas City Royals", league="MLB",
        card_name="Bo Jackson", card_number="300",
    ))

    # 14. 1990 Topps #570
    rows.append(make_row(
        custom_label="BOJACK-14",
        title="1990 Topps #570 Bo Jackson Kansas City Royals Baseball Card",
        description="1990 Topps #570 Bo Jackson - Kansas City Royals. Diagonal name banner design. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="1.99", sport="Baseball", player="Bo Jackson",
        season="1990", year="1990", manufacturer="Topps",
        card_set="Topps", team="Kansas City Royals", league="MLB",
        card_name="Bo Jackson", card_number="570",
    ))

    # 15. 1990 Topps #690
    rows.append(make_row(
        custom_label="BOJACK-15",
        title="1990 Topps #690 Bo Jackson Chicago White Sox Baseball Card",
        description="1990 Topps #690 Bo Jackson - Chicago White Sox. Bat-on-shoulder portrait. Card is ungraded raw. Ships in top loader and rigid mailer.",
        price="2.49", sport="Baseball", player="Bo Jackson",
        season="1990", year="1990", manufacturer="Topps",
        card_set="Topps", team="Chicago White Sox", league="MLB",
        card_name="Bo Jackson", card_number="690",
    ))

    return rows


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    rows = bo_jackson_lot()
    write_csv(rows, "ebay_uploads/bo_jackson_lot.csv")

    # Verify column counts
    with open("ebay_uploads/bo_jackson_lot.csv", encoding="utf-8") as f:
        import csv as c
        reader = c.reader(f)
        next(reader)  # skip info row
        header = next(reader)
        for i, row in enumerate(reader, 1):
            if len(row) != len(header):
                print(f"  ROW {i} MISMATCH: {len(row)} vs {len(header)} header cols")
                break
        else:
            print(f"  All {i} rows match header ({len(header)} cols each)")
