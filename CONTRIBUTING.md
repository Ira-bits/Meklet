# Contributing Guidelines

We love contributions and would be glad to help you make good patches. That out of the way, an average contribution would involve the following:

1. Fork this repository in your account.
2. Clone it on your local machine.
3. Add a new remote using `git remote add upstream https://github.com/Ira-bits/Meklet.git`.
4. Create a new feature branch with `git checkout -b my-feature`.
5. Make your changes.
6. Commit your changes (See [Guidelines](#commit-message-guidelines)).
7. Rebase your commits with `upstream/main`:
  - `git checkout main`
  - `git fetch upstream master`
  - `git reset --hard FETCH_HEAD`
  - `git checkout my-feature`
  - `git rebase main`
8. Resolve any merge conflicts, and then push the branch with `git push origin my-feature`.
9. Create a Pull Request detailing the changes you made and wait for review/merge.

It might seem a little complicated at a glance, but the fundamental concept is simple: we want to ensure that your changes are always made on top of the latest changes to the project and thus, we can easily merge your code. If you are facing any troubles, create a PR as you usually would and we would merge it manually. :)

### Commit Message Guidelines
- Use the present tense ("Add feature" not "Added feature")
- Use imperative mood (e.g., "Fix ...", "Add ..." instead of "Fixes ...", "Adds ...")
- Limit the first line to 72 characters or less
- Keep it short, while concisely explaining what the commit does. 
- Message should be clear about what part of the code is affected -- often by prefixing with the name of the subsystem and a colon, like "backend: ..." or "docs: ...".
- First line should NOT end with a period.
- Reference the relevant Issue or Pull Request in a new line at the end of the message. 

