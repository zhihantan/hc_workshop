**Feedback**

**Section 01 Data Analysis**

- Explain what is fpd5. First Payment Default?
- Why are there so many markdown files? We need to remove the noise from participants. [Exercises.md](http://Exercises.md) , expected-results.md, [facilitator-guide.md](http://facilitator-guide.md), [readme.md](http://readme.md) ? Everything should essentially be viewable from the python file. I want to minimise the context switching for participants.
- Slide-outline should eventually be removed once we're done.
- In part 2 of this section, there is a direction to explore with pyspark. But as part of the workshop, we should be giving reasons for why we need to explore this. Same for part 3, we say explore with SQL, but there isn't a continuation as part of the storyline on why we are exploring here.
- Part 4 follows the same fault - why are you saying build the FPD5 population. First explain some part of the story like as analyst we need have been tasked to find out which loans have defaulted and need our attention. Now it just feels like running cells. We need to follow some logic for the team to also follow.
- The connection between part 4 and part 5 is not clear. We don't even discuss what is eligible first. And what is the point of part 5? What are we exploring?
- It might be better if we start out section with some clarity on the goal.
- In part 6, the cell block is too long. It emcompasses too many things at once. The logic should be separated so that participants can run cell by cell and learn what they are running.
- Can you explain what is the checkpoint at the end? If this is something for the facilitator to explain then let's leave it out of the notebook. If not, let's frame it as some things to think about.
- Remove any content that is meant for facilitator and not for participants.

**Notes for Sean**

- You need to understand the differences in the Spark code here, and the Spark code inside Cloudera. Basically, here a lot of things are managed for you. E.g there is no SparkContext? no SparkSession? Why is that?
- When the cell is %sql - is this running warehouse compute or is this running your all purpose compute?
