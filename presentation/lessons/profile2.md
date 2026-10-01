# 💡 Profile 2

**Tighten It with What Actually Bit.** The profile from Part 1 has carried a day of real work.
You know which grants you needed, which denies got in the way, and which never fired.

----

## Grant it and move on

<img src="assets/images/turnoff-us-permission-issue.png" alt="a patient complains of lacking permissions and is referred to a support group called sudoers" class="comic">

<p class="credit">Daniel Stori · turnoff.us/geek/permission-issue · CC BY-NC-SA 4.0</p>

----

## Read your own log

- Which grants did you add under pressure?
- Which denies never fired?
- Which one blocked work and got worked around?

----

## Tighten, keep working

- Remove grants you did not need
- Narrow the domains to what the build needs
- A profile you disable is worth nothing

----

## Name the holes you keep

- A reachable docker socket is host access
- An allowed domain is a capability, not a destination
- Write each hole into the file

---

## 🛠️ Profile 2

Make the profile small enough to take home.

1. Diff your profile against the commit that ended Part 1.
2. Remove every grant that no task since then needed.
3. Run your track's full check inside the tightened profile.
4. One comment per remaining hole, in the file.

**Done when**

- [ ] smaller than after Part 1, and the work still runs
- [ ] every remaining grant has a reason in the file
- [ ] you would paste this into your team's repository tomorrow
