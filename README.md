# Brightline Plumbing: Lead Service

Take-home task for the Forward Deployed Engineer role at AgileMorph.

**Time limit: 4 hours. Cost to you: nothing.** You don't need any paid tool, API key or subscription. Details under "Tools" below.

## The client

Brightline Plumbing is a 12-person plumbing company in Austin, Texas. Every lead from their website form goes to this service. It:

1. Receives the form submission as a webhook from their form builder
2. Asks an LLM to tag urgency (emergency, soon, routine) and draft a short SMS reply
3. Saves the lead to the database
4. Texts the customer

A previous contractor built it quickly about a month ago. It runs in Docker on a small cloud VM. Mike, the owner, checks the `/leads` endpoint through a simple internal page.

**It's live.** `data/prod_snapshot.db` is a copy of the production database from yesterday. It holds 3 weeks of real leads, with names and numbers changed. Anything you change has to work on that database without losing a lead.

Mike sent us this last week:

> "Few things. Some customers are getting the same text 2 or 3 times, which looks bad. Last Tuesday a lady with water coming through her ceiling got tagged routine and nobody called her till the next morning. And honestly I don't know if the after-hours stuff works at all."

## Setup (about 10 minutes)

You need Python 3.11 or newer.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second terminal, replay the sample leads the way the form builder sends them:

```bash
python scripts/simulate_form_provider.py
```

Mock texts go to `data/sms_outbox.jsonl`. Leads are at `http://localhost:8000/leads`. Run the tests with `pytest`. To run against production data, copy the snapshot first and point the service at the copy:

```bash
cp data/prod_snapshot.db data/working.db
BRIGHTLINE_DB=data/working.db uvicorn app.main:app --reload
```

## Time budget

| Part | Time |
| --- | --- |
| Setup and reading the code | 20 min |
| Subtask A | 1 hr 40 min |
| Subtask B | 1 hr 30 min |
| Notes | 30 min |

Stop at 4 hours, even if you're not done. Write down what you'd do next and send what you have.

## Subtask A: Audit and fix (about 1 hr 40 min)

1. Find what's behind Mike's three complaints, plus anything else you'd flag. Rank every issue by its impact on Mike's business.
2. Fix the top two issues, with tests that would have caught them.
3. Your fixes have to work on the live database. Include whatever it takes to apply them to `data/prod_snapshot.db` safely, and tell us what you did with any bad data already in it.

## Subtask B: New request (about 1 hr 30 min)

Mike sent a voice note:

> "OK so new thing. When somebody has a real emergency at night, like a burst pipe or sewage backing up, I want whoever's on call to get a text right away. Not for a drippy faucet though, I don't want my guys woken up for that. And can I get some kind of summary every Monday of how many leads we got and what kind, in my email. Thanks."

An hour later, Rosa, his office manager, emailed us. Mike hasn't seen it:

> "Hi, saw Mike's note. Please don't have it text the techs directly at night. Last month Danny got woken up for a leaky hose bib and almost quit. Can it text me and I'll decide who to send? I'm usually up till midnight."

1. **Spec.** Write a one-page `SPEC.md` for both requests. Decide what to do about Rosa's email and explain why. List the questions you'd ask and the assumptions you'll use until you get answers.
2. **Build the night emergency alert only.** The Monday summary stays in the spec. Don't build it.
3. **Test the classifier.** Write at least 12 realistic lead messages with the urgency you expect for each, including tricky ones. Run them and report how many pass, and on which model.

## Questions

Some facts you'll need aren't in this repo. Email hr@theagilemorph.com and we'll answer during Indian working hours. If you don't want to wait, write down your assumption and keep going. Both are fine. We look at which gaps you noticed.

## Tools

- **AI coding tools:** use whatever you normally use. Free options work fine, like the free tiers of Claude, ChatGPT, Gemini CLI, GitHub Copilot or Cursor.
- **The LLM inside the service:** mock mode needs nothing and is enough for Subtask A. For the classifier test in Subtask B, use a free real model if you can:
    - **Local with Ollama (no key, no cost):** install [Ollama](https://ollama.com), run `ollama pull llama3.2`, then start the service with `LLM_MODE=openai_compat`.
    - **A free-tier key of your own,** for example from Google AI Studio or Groq. Set `LLM_MODE=openai_compat`, plus `LLM_BASE_URL`, `LLM_MODEL` and `LLM_API_KEY` for that provider's OpenAI-compatible endpoint.
    - If neither works on your machine, run the classifier test in mock mode and tell us. We grade how you built the test, not the score.
- Never commit keys.

## Getting the repo and sending your work

Keep your work private. GitHub doesn't allow private forks of a public repo, so use one of these instead:

- **Use this template:** click **Use this template** at the top of this repo, choose **Create a new repository**, and set it to **Private**.
- **Or clone and push:** create an empty private repo on your account, then:

```bash
git clone https://github.com/umangd98/Take-Home-Task.git
cd Take-Home-Task
git remote set-url origin https://github.com/<you>/<your-private-repo>.git
git push -u origin main
```

When you're done, add **kaustumbh7** as a collaborator (Settings, then Collaborators), and email us the link. Commit as you go, since we read the history.

## What to send

1. Your private repo, shared with kaustumbh7
2. `NOTES.md` with two parts:
    - **For Mike:** what went wrong and what you changed, in plain English, under 150 words
    - **For our team:** every issue you found, its cause, what you did about the live data, and what you'd fix next
3. `SPEC.md`
4. An `ai-logs/` folder with your raw AI sessions: an export, a share link or a copy-paste of the full chat. Summaries don't count. Messy logs are fine, since we want to see how you actually work.
5. A Loom of 5 minutes or less walking us through your work. Loom's free plan is enough.
