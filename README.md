# Premise

Here's an oddball investigation inspired by a gut feeling of mine: all of Trea Turner's home runs look exactly the same. I'm not even a Phillies fan and yet I can picture them so clearly: belt-high fastball, middle to middle-out, 29 degree launch angle and 106mph exit velocity. 408 feet to left-center, 5 rows back. Every time, I swear!

This got me thinking about to what extent we can quantify and identify home runs that really do look about the same. More specifically, how often do players hit _consecutive_, near-identical homers? And most importantly, is there any basis for my weird convictions about Trea Turner?

# Approach

Since Statcast gives us the X-Y coordinates for where each homer lands, this can be treated as a case of the [smallest-circle problem](https://en.wikipedia.org/wiki/Smallest-circle_problem). Think of it as having a big basketball hoop out in the bleachers. How wide would the basket need to be be for us to find an instance of a specific player hitting 2 (or 3, or 4) consecutive baskets? The home runs need not be consecutive _plate appearances_, only consecutive in their season totals (i.e. homers 16 through 18 or whatever).

This can identify oddities like Starling Marte's 2nd and 3rd homers of 2024, both of which doinked off of nearly the exact same length of guardrail at Citi Field:

- [Homer #2](https://baseballsavant.mlb.com/sporty-videos?playId=2c3f8ae4-002a-4667-9754-26fbfc9d08b9)
- [Homer #3](https://baseballsavant.mlb.com/sporty-videos?playId=c40d96ca-a2d1-4fe1-8dab-a7f0cba603c2)

This is a fantastic and strange achievement, but it's not quite what I'm looking for - these homers don't _look_ the same. The first is a line drive that stays within the frame the whole time, the second a high fly ball. How can we take this further?

# Formula

I'm going to propose a new metric-to-be-named-later. This metric considers a group of N consecutive home runs to look most similar when:

- They land within a small area
- They're confined to a small range of exit velocities and launch angles
- The pitches are confined to a small area of the strike zone

Beyond the stats for each homer, some contextual elements are also very important:

- Homers hit in the same stadium look more similar
- Homers hit off the same pitcher look more similar
- Homers hit in the same game _feel_ more similar

And thus I've arrived at the following formula for calculating this unit-less "similarity score":

    similarity = 100 - (deductions/(1 + bonuses))

        where "deductions" are defined as the sum of:
            radius of the smallest enclosing circle
            range of launch angles
            range of exit velocities
            range of horizontal positions of pitches
            range of vertical positions of pitches

        and "bonuses" are defined as the sum of:
            2 if all homers were hit in the same stadium, else 0
            0.5 if all homers were hit in the same game, else 0
            0.5 if all homers were hit off the same pitcher, else 0

A group of completely identical homers would get a score of 100. Note that being hit in the same stadium is especially important! I got a little tired of watching homers that are statistically similar, but the apples-to-oranges comparison doesn't allow them to look that similar.

# Results

Without further ado, here is my leaderboard for the 2024 homers that all look the same-est.

### OUR CHAMPION: Kyle Manzardo

**Kyle Manzardo** scored a whopping **99.07** for homers 1 and 2. These homers were hit to nearly the exact same location, looked about the same off the bat, and were both hit off Mitch Keller on September 1st:

- [Manzardo #1](https://baseballsavant.mlb.com/sporty-videos?playId=fdd92d4e-21c2-4c55-94e7-8814957968b2)
- [Manzardo #2](https://baseballsavant.mlb.com/sporty-videos?playId=0512c2a2-e22e-4fd2-aa92-673ab31df404)

Not only that, these were Kyle's first two _career_ home runs. What auspicious beginnings! I'm sure they're still fresh in his memory, and now they're fresh in ours. Please join me today in congratulating Mr. Manzardo!

**RUNNERS UP**

**Christian Walker** scored a **98.89** for homers 24 and 25, both off Nate Eovaldi on September 10th:

- [Walker #24](https://baseballsavant.mlb.com/sporty-videos?playId=2d810867-8e8b-4bf5-ba41-e5d1929fa232)
- [Walker #25](https://baseballsavant.mlb.com/sporty-videos?playId=ccd77710-7e4f-4b78-9c37-4a72ba61e174)

I love this pair because each must've been tough for Eovaldi to watch barely sneak over the right field fence. Two such identical shots by the 3rd inning, by the same guy?? Just devastating and weird.

---

**Zach Gelof** scored a **98.67** for homers 7 and 8. This is the highest-scoring pair that wasn't given the bonus of being hit in the same game! Instead, Gelof scores so highly due to sheer consistency: #7 had a launch angle of 27 degrees and 105.9 exit velo, while #8 had a launch angle of _28_ degrees and 105.9 exit velo:

- [Gelof #7](https://baseballsavant.mlb.com/sporty-videos?playId=edd7cb32-49d6-440d-8274-7d5c113e33ed)
- [Gelof #8](https://baseballsavant.mlb.com/sporty-videos?playId=f3aa44a9-1cff-4432-b408-f2acce5bec3a)

These two might look the most similar for my money, but I have a responsibility to honor the numbers here and this is ultimately a post about Kyle Manzardo.

## Honorable Mentions

Unsurprisingly, the most identical-looking groups of consecutive home runs all come in groups of 2. It quickly becomes much less likely for a player to hit 3, 4, or 5 straight homers that all look about the same, and the results get less interesting. However, I still wanted to honor a few exceptions that I liked:

**J.D. Martinez** scored a **95.32** for his homers 6 through 8, all hit at Citi Field over 2 games in June:

- [Martinez #6](https://baseballsavant.mlb.com/sporty-videos?playId=1abe2736-6985-4707-80e0-19c7ce824876)
- [Martinez #7](https://baseballsavant.mlb.com/sporty-videos?playId=2b361315-5ec6-49fd-b561-77d064c3b2e9)
- [Martinez #8](https://baseballsavant.mlb.com/sporty-videos?playId=0366c73c-e5fd-43db-8bf8-e6551c88b981)

As a Red Sox fan, I fully agree that each of these 3 is a canonical J.D. Martinez homer.

---

**Mookie Betts** scored a **92.87** for home runs 16 through 19. Somewhat remarkably, none of these four exceeded 100mph in exit velocity:

- [Betts #16](https://baseballsavant.mlb.com/sporty-videos?playId=85c13077-d374-4bce-b441-96990354091d)
- [Betts #17](https://baseballsavant.mlb.com/sporty-videos?playId=333de268-eea3-4bb3-bf5a-4c2d5210f971)
- [Betts #18](https://baseballsavant.mlb.com/sporty-videos?playId=1b78e781-b46a-4216-bc7d-783b7f476cbf)
- [Betts #19](https://baseballsavant.mlb.com/sporty-videos?playId=ef06b278-f0ed-4950-a33f-771807f1ed81)

As a Red Sox fan, it still hurts.

# Conclusions

Baseball is fun, and I found no evidence supporting my claim that Trea Turner only hits one kind of home run. I'm sorry Trea!

Furthermore, I propose that this metric be named after our first annual champion: **The Manzardo Score**.

## Source code

This project was done with a CSV export from Baseball Savant and a bit of Python. The code, the source data, and the full set of results can all be found [here on Github]().

## Addendum

It's also somewhat interesting to look at groups of homers that have the lowest Manzardo scores to see who's hitting the most dissimilar, consecutive home runs. For groups of N consecutive home runs 2 through 10, each of those leaders are: Bryce Harper, Rafael Devers, Rafael Devers, Yordan Alvarez, Yordan Alvarez, Yordan Alvarez, Yordan Alvarez, Oneil Cruz, Oneil Cruz. This make sense; these are all guys that have enough power to flick a looping fly ball over the opposite field fence, and then hit you next time with a 450ft, 115mph missle down the other line.
