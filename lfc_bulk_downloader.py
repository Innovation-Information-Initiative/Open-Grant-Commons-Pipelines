# -*- coding: utf-8 -*-
"""
NOTES:
    - Data fields contain OrderedDicts with the Comments field, a list of comments per Judge
    - Convert all OrderedDicts to json strings
    - Convert all lists to comma-separated strings
"""

FIELDS = [
    "Application #",
    "Competition Domain",
    "Project Title",
    "Organization Name",
    "Organization Location",
    "Executive Summary",
    "Project Description",
    "Key Words and Phrases",
    "Primary Subject Area",
    "Annual Operating Budget",
    "Number of Employees",
    "Project Website",
    "Total Projected Costs",
    "Sustainable Development Goals",
    "Priority Populations",
    "Achievement Level",
    "LFC Financial Data",
    "LFC Analysis",
    "Panel Score",
    "Rank",
    "Peer Score",
    "Panel Rank",
    "Panel EVIDENCE-BASED Score Normalized",
    "Panel FEASIBLE Score Normalized",
    "Panel IMPACTFUL Score Normalized",
    "Panel COMMUNITY-INFORMED Score Normalized",
    "Panel SCALABLE Score Normalized",
    "Panel EQUITABLE Score Normalized",
    "Panel ACTIONABLE Score Normalized",
    "Panel BOLD Score Normalized",
    "Panel INNOVATIVE Score Normalized",
    "Panel TRANSFORMATIVE Score Normalized",
    "Panel DURABLE Score Normalized",
    "Panel DURABLE Judge Data",
    "Panel EVIDENCE-BASED Judge Data",
    "Panel FEASIBLE Judge Data",
    "Panel IMPACTFUL Judge Data",
    "Panel COMMUNITY-INFORMED Judge Data",
    "Panel SCALABLE Judge Data",
    "Panel EQUITABLE Judge Data",
    "Panel ACTIONABLE Judge Data",
    "Panel BOLD Judge Data",
    "Panel INNOVATIVE Judge Data",
    "Panel TRANSFORMATIVE Judge Data",
    "Peer EVIDENCE-BASED Score Normalized",
    "Peer FEASIBLE Score Normalized",
    "Peer IMPACTFUL Score Normalized",
    "Peer COMMUNITY-INFORMED Score Normalized",
    "Peer SCALABLE Score Normalized",
    "Peer EQUITABLE Score Normalized",
    "Peer ACTIONABLE Score Normalized",
    "Peer BOLD Score Normalized",
    "Peer INNOVATIVE Score Normalized",
    "Peer TRANFORMATIVE Score Normalized",
    "Peer Sum of Scores Normalized",
    "Peer DURABLE Judge Data",
    "Peer EVIDENCE-BASED Judge Data",
    "Peer FEASIBLE Judge Data",
    "Peer IMPACTIFUL Judge Data",
    "Peer COMMUNITY-INFORMED Judge Data",
    "Peer SCALABLE Judge Data",
    "Peer EQUITABLE Judge Data",
    "Peer ACTIONABLE Judge Data",
    "Peer BOLD Judge Data",
    "Peer INNOVATIVE Judge Data",
    "Peer TRANSFORMATIVE Judge Data",
]

import mwclient
import time
import json
import asyncio
import re
import html
import pandas as pd
from collections import OrderedDict


def get_proposals(site, proposals):

    df = []

    # For each proposal, get all fields
    for c, id_ in proposals:

        print(f"Adding proposal {id_} from competition {c}")

        prop = site.api(
            "torquedataconnect",
            format="json",
            path=f"/competitions/{c}/proposals/{id_}",
        )["result"]

        # Grab desired fields
        tmp = {}
        for field in FIELDS:

            val = prop.get(field)

            # Clean val if it's a data-structure
            if isinstance(val, list):
                try:
                    val = ", ".join(val)
                except:
                    val = None

            elif isinstance(val, OrderedDict):

                if "Score" in field:
                    try:
                        val = float(val.get("Raw"))
                    except:
                        val = None
                else:
                    val = json.dumps(val)

            elif field == "Applicant Tax Identification Number" and val:
                val = re.sub("[^0-9]", "", str(val))

                if val:
                    val = int(val)
                else:
                    val = None

            elif isinstance(val, str):

                val = html.unescape(val)

                # Clean rich text data
                if len(val) > 25 and field != "Project Website":
                    val = re.sub(" {2,}", " ", re.sub("(<[^<>]{0,}>)", " ", val))
                else:
                    na = ["Not Applicable", "N/A", "N/a", "n/a"]
                    if any(val.startswith(s) for s in na):
                        val = ""
                    elif any(val == s for s in ["na", "NA", "Na", "None"]):
                        val = ""

            if field == "Competition Domain":
                tmp["Competition"] = c
            else:
                tmp[field] = val

        df.append(tmp)

    return df


async def main(username, api_key):

    site = mwclient.Site("torque.leverforchange.org/", "GlobalView/", scheme="https")
    site.login(username, api_key)

    t0 = time.time()

    # Get all Competition titles
    competitions = site.api("torquedataconnect", format="json", path="/competitions")[
        "result"
    ]

    print([c for c in competitions])

    # Get a list of tuples representing all (competition, id) pairs
    proposal_ids = []
    for c in competitions:
        proposals = site.api(
            "torquedataconnect", format="json", path=f"/competitions/{c}/proposals"
        )["result"]
        pairs = [(c, id_) for id_ in proposals]
        proposal_ids.extend(pairs)
    proposal_ids = list(set(proposal_ids))  # remove duplicates just in case

    # Split of ist of proposals ids
    threads = 20
    step = len(proposal_ids) // threads
    chopped_ids = [proposal_ids[i * step : step * (i + 1) + 1] for i in range(threads)]

    """
    tasks = [
        asyncio.to_thread(
            lambda: get_proposals(site, chopped_ids[i])
            ) for i in range(len(chopped_ids))
        ]

    For some reason, the asyncio.to_thread() method won't work with generator statements
    So unfortunately I had to manually map the list slices into each thread

    """
    res = await asyncio.gather(
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[0])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[1])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[2])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[3])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[4])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[5])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[6])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[7])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[8])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[9])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[10])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[11])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[12])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[13])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[14])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[15])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[16])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[17])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[18])),
        asyncio.to_thread(lambda: get_proposals(site, chopped_ids[19])),
    )
    df = [x for r in res for x in r]

    t = round(time.time() - t0, 0)
    print(f"Finished in {t} seconds")

    df = pd.DataFrame(df)
    df.to_csv("LFC_Proposals.csv", index=False)


if __name__ == "__main__":

    username = str(input("Please enter your MediaWiki username: "))
    api_key = str(input("Please enter your MediaWiki API key: "))

    asyncio.run(main(username, api_key))