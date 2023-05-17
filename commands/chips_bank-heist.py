def chips_bank_heist_get_rolls(interaction):
    amount = interaction.data["custom_id"].split("n=d")[1].split(";")[0]
    roll = random.randint(1, int(amount))
    all_rolls = []
    if "rolls=" in interaction.data["custom_id"]:
        all_rolls = [int(x) for x in interaction.data["custom_id"].split("rolls=")[-1].split(",")]
    all_rolls.append(roll)
    if "stage=3;" in interaction.data["custom_id"]:
        return f"> *You rolled a `{roll}`*\n", roll, all_rolls
    return f"> *You rolled a `{roll}` [d{amount}]*\n", roll, all_rolls

def chips_bank_heist_rng_view(interaction, amount, next_stage, *, rolls = [], view = None, label = None):
    if view is None:
        view = discord.ui.View(timeout = None)
    if label is None:
        label = f"Continue mission"
    custom_id = f"chips-bank={interaction.user.id};n={amount};stage={next_stage}"
    if rolls:
        custom_id += f";rolls={','.join(str(x) for x in rolls)}"
    view.add_item(discord.ui.Button(label = label, custom_id = custom_id))
    return view

def chips_bank_heist_fail(interaction):
    open(ROOT_DATA + "jailed/" + str(interaction.user.id), "w+").write("")

def chips_bank_heist_success():
    last_time = int(open(ROOT_DATA + "bank_rob_time").read())
    this_time = int(get_time())
    rewards = (this_time - last_time) * 2
    open(ROOT_DATA + "bank_rob_time", "w+").write(str(this_time))
    return rewards

def chips_bank_heist_stage_0(interaction):
    last_time = int(open(ROOT_DATA + "bank_rob_time").read())
    this_time = int(get_time())
    msg = ""
    if (this_time - last_time) * 2 < 500:
        msg = f"You follow the news closely, and remember that the bank was last robbed <t:{last_time}:R>, which is "
        msg += "far too short of a time to make any substantial earnings. But, you are too excited to try out your new "
        msg += "strategy and press on.\n\n"
    msg += "You are getting ready for your heist. You have your mask and your bag, and start walking out the door. " +\
            "At that moment, you realize you forgot your gun. You have plenty of real ones and fake models all scattered about..."

    view = chips_bank_heist_rng_view(interaction, "d12", "1")
    return msg, view

def chips_bank_heist_stage_1(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    if roll < 4:
        msg += "You grab the first gun in sight. It feels lighter than normal but you pay no mind to that..."
    elif roll < 6:
        msg += "You start rummaging through your firearms, you pick up a light one but realize it is fake. " + \
                "Quickly, you pick up another, and it is real. You hurry out the door..."
    else:
        msg += "You grab the first gun in sight. Your hand feels cold as you hurry out the door..."
    msg += "\n\nYou enter the lobby of your local bank, and look for security guards on duty..."

    view = chips_bank_heist_rng_view(interaction, "d20", "2")
    return msg, view

def chips_bank_heist_stage_2(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    if roll < 7:
        msg += "As you step foot in the bank, you peer around and find a guard in a very light sleep..."
    elif roll < 16:
        msg += "Walking into the lobby, you find the guard sitting up straight, head back and eyes closed. "
        msg += "You walk up to him and assume he is taking a nap..."
    else:
        msg += "The lobby is completely silent, and completely empty. You scan the room to find the guard dead "
        msg += "asleep in the corner. Puzzled, you decide to move past him."
    view = chips_bank_heist_rng_view(interaction, "d6", "3", rolls = all_rolls, label = "Run to teller")
    chips_bank_heist_rng_view(interaction, "d12", "3", rolls = all_rolls, view = view, label = "Walk casually")
    chips_bank_heist_rng_view(interaction, "d20", "3", rolls = all_rolls, view = view, label = "Tip-toe past guard")

    return msg, view

def chips_bank_heist_stage_3(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    if roll < 4:
        msg += "Nervous, you develop sweaty palms "
    if roll < 2:
        msg += "and drop your gun, and a crashing sound echoes throughout the hall. "
        if all_rolls[1] < 16:
            msg += "Startled by the sound, you pick up your gun and make a run for the exit. The napping cop from "
            msg += "before wakes up and starts sprinting your way, as he yells *\"We've got a code `64`\"* into the "
            msg += "walkie-talkie. You turn your head to see him gaining on you quickly..."
            view = chips_bank_heist_rng_view(interaction, "d6", "3FB", rolls = all_rolls, label = "Escape")
        else:
            msg += "Suddenly, a voice emerges from behind you. Startled, you listen closely: *\"No bank robbing too-daayyyy...\"* "
            msg += "You sigh in relief knowing that he is still sleeping, but are more cautious now that he is barely awake. "
            msg += "You slowly move towards the floor to retrieve your weapon, and continue making your way to the teller... "
            all_rolls[1] = 4
            view = chips_bank_heist_rng_view(interaction, "d8", "4", rolls = all_rolls)
    elif roll < 3:
        msg += "and lose grip of your gun, so you fumble about trying to stop it from falling on the floor. "
        if all_rolls[1] < 7:
            msg += "All this moving about made some rattling sounds, loud enough to wake up the barely sleeping officer "
            msg += "from before. You turn around slowly, keeping a smile on your face. As you refocus your eyes, you immediately "
            msg += "jump back from the barrel that was staring you down. With a whimpering whisper, you let out a small '*hi*', "
            msg += "as you make your next decision..."
            view = chips_bank_heist_rng_view(interaction, "d6", "3FB", rolls = all_rolls, label = "Escape")
            chips_bank_heist_rng_view(interaction, "d4", "3FA", rolls = all_rolls, view = view, label = "Distraction technique")
        else:
            msg += "Suddenly, a growl emerges from the back corner of the room. Quickly, you look in the direction of "
            msg += "the noise, and are relieved to see the cop is still sleeping, but just lightly so. You watch as he "
            msg += "readjusts himself to make sure he stays asleep, as you continue towards the teller... "
            all_rolls[1] = 4
            view = chips_bank_heist_rng_view(interaction, "d8", "4", rolls = all_rolls)
    elif roll < 6:
        msg += "As you walk through the spacious lobby, a pen suddenly falls out of your pocket. "
        if all_rolls[1] < 7:
            msg += "Quickly, but silently, you bend over to pick up the pen. As you stand back up, you can feel an eerie "
            msg += "presence behind you, almost as if someone is breathing down your neck. Slowly, you turn around, keeping "
            msg += "your eyes on the floor. First the boots, then the deep blue pants, and a sinking feeling kicks in. "
            msg += "You look up and refocus your eyes to see the end of a barrel staring at you square in the face. "
            msg += "You muster out a quiet *'hi'* as you make your next decision..."
            view = chips_bank_heist_rng_view(interaction, "d6", "3FB", rolls = all_rolls, label = "Escape")
            chips_bank_heist_rng_view(interaction, "d4", "3FA", rolls = all_rolls, view = view, label = "Distraction technique")
        elif all_rolls[1] < 16:
            msg += "Suddenly, a growl emerges from the back corner of the room. Quickly, you look in the direction of "
            msg += "the noise, and are relieved to see the cop is still sleeping, but just lightly so. You watch as he "
            msg += "readjusts himself to make sure he stays asleep, as you continue towards the teller... "
            all_rolls[1] = 4
            view = chips_bank_heist_rng_view(interaction, "d8", "4", rolls = all_rolls)
        else:
            msg += "Confidently, you pick up the pen from before. There is nothing to worry about since the officer is "
            msg += "dreaming about "
            match random.randint(1, 6):
                case 1:
                    msg += "rainbows and unicorns. "
                case 2:
                    msg += "roses and daisies. "
                case 3:
                    msg += "being surrounded by cute, fluffy cats. "
                case 4:
                    msg += "the smiles on his kids' and wife's faces. "
                case 5:
                    msg += "a beach vacation he could never afford. "
                case 6:
                    msg += "that sweet new game coming out tomorrow. "
            msg += "So, you press on..."
            view = chips_bank_heist_rng_view(interaction, "d8", "4", rolls = all_rolls)
    else:
        msg += "Keeping calm and collected, you confidently make your way to the teller. Readjusting your mask, gun in "
        msg += "one hand, and bag in the other. Everything was going well so far..."
        view = chips_bank_heist_rng_view(interaction, "d8", "4", rolls = all_rolls)

    return msg, view

def chips_bank_heist_stage_3FA(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    view = discord.ui.View(timeout = None)
    msg += "You rather cartoonishly point out at the window and yell *\"Hey, what's that!\"* in an attempt to distract "
    msg += "the officer. "
    if roll == 4:
        msg += "Incredibly, he falls for it. Perhaps he was a bit too sleepy. Either way, he spends just enough time "
        msg += "looking around aimlessly for you to make a quiet and successful escape.\n\n"
        color = 0xffff00
        msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Escaped\n"
    else:
        msg += "Unsurprisingly, he doesn't fall for it. You let out a soft sigh and turn yourself in.\n\n"
        msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
        color = 0xff0000
        chips_bank_heist_fail(interaction)
    return msg, view, color

def chips_bank_heist_stage_3FB(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    view = discord.ui.View(timeout = None)
    branch = random.randint(1, 4)
    msg += "You make a break for the nearest exit while you can, "
    heist_meme = False
    if roll > 4:
        color = 0xffff00
    else:
        color = 0xff0000
        chips_bank_heist_fail(interaction)
    if branch == 1:
        count = random.randint(3, 7)
        msg += "The cop starts shooting at you. You quickly make a dodge "
        msg += ", ".join(random.choice(["left", "right"]) for x in range(count)) + "! "
        if roll > 4:
            msg += "Remarkably, you miss all the bullets and outrun the cops.\n\n"
            msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Escaped\n"
        else:
            msg += "However, no matter the dodges you make, those bullets just came to quickly, and "
            msg += str(random.randint(1, count)) + " of them hit you. You collapse to the ground, slowly bleeding away. "
            msg += "Your vision turns all fuzzy, as you hear voices and see flashing amber lights. "
            msg += "You wake up in a hospital bed, surrounded by police.\n\n"
            msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
    elif branch == 2:
        msg += "You make your way down a dark alley. You take some advice from cartoons and make a sharp turn around a corner. "
        if roll > 4:
            msg += "Astoundingly, the officer runs right passed you, so you make your successful escape. "
            msg += "You struggle to contain your laughter.\n\n"
            msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Escaped\n"
        else:
            msg += "However, unlike in those cartoons, the officer doesn't fall for it and finds you immediately.\n\n"
            msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
    elif branch == 3:
        msg += "Frightened, you quickly point and shoot your weapon, and "
        if roll > 4 and all_rolls[1] >= 4:
            msg += "hit the square in the face. You quickly make your successful escape\n\n"
            msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Escaped\n"
        else:
            msg += "miss completely. He decides to copy you, but hits you square in the chest with a rubber bullet. "
            msg += "You collapse backwards drop to the floor.\n\n"
            msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
    elif branch == 4:
        msg += "You have never been confident in your skills, and trained diligently for this special occasion, "
        heist_meme = True
        if roll > 4:
            msg += "which paid off substantially. The cop soon gets tired and you immediately outrun him, successfully escaping.\n\n"
            msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Escaped\n"
        else:
            msg += "which unfortunately didn't pay off. Your stamina was far too low, and the officer caught up to you "
            msg += "very quickly. It didn't take much time before you blacked out from over-exertion.\n\n"
            msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"

    return msg, view, color, heist_meme

def chips_bank_heist_stage_5(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    msg += "You scramble to stuff as many chips inside the bag as possible. Soon after you trip the alarm, faint sirens "
    msg += "begin to sound from the distance. Minutes later, the light in the vault slightly flickers between red and blue. "
    msg += "Frightened, you immediately close the bag and make your way to the exit. As you pass by the teller, you "
    msg += "thank her for her cooperation, and continue to the car. Unfortunately, in the rush, you could only load "
    msg += f"about {5 * roll}% of the chips in the bag."
    view = chips_bank_heist_rng_view(interaction, "d20", "6", rolls = all_rolls, label = "Head out to car")

    return msg, view

def chips_bank_heist_stage_4(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    msg += "As you walk up to the teller, you strongly lift your right arm, making sure the weapon was facing her. "
    if roll == 1:
        msg += "But, an unexpected turn of events leads her magically producing her own weapon from behind the counter. "
        msg += "She lets out a massive cry to wake up the officer. Immediately, you readjust your stance as you scan the "
        msg += "room to make an escape."
        view = chips_bank_heist_rng_view(interaction, "d6", "3FB", rolls = all_rolls, label = "Escape")
    else:
        msg += "Frightened, she immediately complies with your demands. After a few seconds of spinning the dial, she swings the "
        msg += "lever down and struggles to open the massive vault door. As you make your way towards the entrance, you "
        msg += "suddenly remember that banks have lasers to detect unauthorized people from entering. You start scavenging "
        msg += "through your bag to find a can of computer duster you may have left behind. "
        if roll == 8:
            msg += "Conveniently enough, you find it, and spray inside the vault to reveal all the lasers. They are "
            msg += "sparsely positioned throughout the room, and you dodge them all with ease. After the bag is filled "
            msg += "to the brim, you make an exit..."
            view = chips_bank_heist_rng_view(interaction, "d4", "4S", rolls = all_rolls, label = "Exit vault")
        else:
            msg += "Unfortunately, you find nothing. Knowing there is no way to avoid the alarm, you spring inside "
            msg += "the vault and immediately start loading the bag..."
            view = chips_bank_heist_rng_view(interaction, "d12", "5", rolls = all_rolls, label = "Load bag")

    return msg, view

def chips_bank_heist_stage_4S(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    view = discord.ui.View(timeout = None)
    msg += "Delighted with the ease of the operation, you make your way out of the vault. As you are about to wish "
    msg += "a farewell to the teller, "
    if roll < 4:
        msg += "you notice that she is pointing a gun straight at your heart. "
        if all_rolls[0] < 4:
            n1 = random.randint(2, 5)
            n2 = random.randint(n1 + 1, n1 + 3)
            msg += "You laugh this off with confidence, and slowly pull out your weapon. Curious about your cackling, "
            msg += "she did not fire quite yet. You make a snarky remark about her weakness, and aim your pistol at her. "
            msg += "But she starts laughing hysterically back at you...\n\n"
            msg += "You but feel no resistance. You keep on pulling the trigger as the feeling of hopelessness sinks in. "
            msg += f"After pulling the trigger {n1}-{n2} times, you finally realize that you are holding a fake gun, and "
            msg += "make a very accentuated face palm. All the commotion woke up the officer, and as he saw the red ring "
            msg += "around the barrel of your pistol, he started laughing too. "

            msg += "An investigation is quickly opened into your history of fraud, and half of your chips are confiscated.\n\n"
            total_chips = give_chips(interaction.user, 0)
            loss = give_chips(interaction.user, -int(total_chips / 2))
            color = 0xff0000
            chips_bank_heist_fail(interaction)

            msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours\n"
            msg += f"**Loss:** {loss}x {DEAD_EMOJI}"

        else:
            msg += "Quickly, you pull out your weapon and shoot her gun away, leaving her unharmed. "
            msg += "You scramble to collect your things, as the officer wakes up to the loud noise. "
            if all_rolls[1] < 7:
                msg += "Since he was in a very light sleep before, he doesn't take long to collect his bearings. He "
                msg += "takes aim and shoots you square in the back in mere seconds.\n\n"
                msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
                color = 0xff0000
                chips_bank_heist_fail(interaction)
            else:
                rewards = chips_bank_heist_success()
                rewards = int(rewards * 0.9)
                color = 0x22cc22
                msg += "Luckily, he takes too long to wake up from his nap. However, due the kerfuffle with the "
                msg += "teller, your bag got stuck in the hinges of the vault. You rip it away, and a small hole is "
                msg += "left behind, costing you 10% of your earnings. Being aware of the officer, you neglect "
                msg += "the chips that fell out of your bag, and quickly rush towards the exit.\n\n"
                msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Reward:** {rewards}x {DEAD_EMOJI} (90% of possible)"
                msg += f"\n**Total Chips:** {give_chips(interaction.user, rewards)}x {DEAD_EMOJI}"
    else:
        rewards = chips_bank_heist_success()
        color = 0x22cc22
        msg += "you notice her cowering in the corner. You pay no mind to her and exit the building, safely.\n\n"
        msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Reward:** {rewards}x {DEAD_EMOJI} (100% turnout!)"
        msg += f"\n**Total Chips:** {give_chips(interaction.user, rewards)}x {DEAD_EMOJI}"

    return msg, view, color

def chips_bank_heist_stage_5(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    msg += "You scramble to stuff as many chips inside the bag as possible. Soon after you trip the alarm, faint sirens "
    msg += "begin to sound from the distance. Minutes later, the light in the vault slightly flickers between red and blue. "
    msg += "Frightened, you immediately close the bag and make your way to the exit. As you pass by the teller, you "
    msg += "thank her for her cooperation, and continue to the car. Unfortunately, in the rush, you could only load "
    msg += f"about {5 * roll}% of the chips in the bag."
    view = chips_bank_heist_rng_view(interaction, "d20", "6", rolls = all_rolls, label = "Head out to car")

    return msg, view

def chips_bank_heist_stage_6(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    msg += "As you exit the bank, the blue and red lights are bright and clear, and the sirens are blaring. "
    msg += "There isn't much time left, so you put your hand on the car door handle, and pull. "
    if roll < 13:
        n1 = random.randint(2, 5)
        n2 = random.randint(n1 + 1, n1 + 3)
        msg += f"But nothing happens. You try {n1}-{n2} more times before realizing your dimwitted self accidentally "
        msg += "locked the car door before the heist. Frantically, you fumble about your pockets, unlock the car, and "
        msg += "hop inside."
    else:
        msg += "You swing the door wide open and throw yourself inside the car, grab the keys from your pocket. "
    msg += "Hastily, you shove the key in the starter, twist, and floor the gas pedal..."
    view = chips_bank_heist_rng_view(interaction, "d20", "7", rolls = all_rolls, label = "Drive away")

    return msg, view

def chips_bank_heist_stage_7(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    msg += "With the pedal to the metal, you look in the rear-view mirror to see a police car behind you. Speeding up "
    msg += "to over 90mph in these city streets, you suddenly swerve " + random.choice(["right", "left"]) + " to find a "
    if roll == 1:
        msg += "dead end. It would take too long to turn the car around, you you immediately think of other solutions to "
        msg += "get out of this predicament. You step out of the car and look around to find a few markets with lights "
        msg += "still open at this late hour..."
        view = chips_bank_heist_rng_view(interaction, "d8", "71A", rolls = all_rolls, label = "Visit: Thrift Store")
        chips_bank_heist_rng_view(interaction, "d12", "71B", rolls = all_rolls, view = view, label = "Visit: Castbrew Coffee")
        chips_bank_heist_rng_view(interaction, "d4", "71C", rolls = all_rolls, view = view, label = "Screw it: Climb up fire stairs")
    elif roll < 12:
        msg += "sea of flashing lights headed straight your way from across a bridge. You quickly make a plan to dodge "
        msg += "the cops..."
        view = chips_bank_heist_rng_view(interaction, "d8", "72A", rolls = all_rolls, label = "Jump using construction ramp")
        chips_bank_heist_rng_view(interaction, "d6", "72B", rolls = all_rolls, view = view, label = "Swerve and dive into river")
    else:
        msg += "a completely clear alleyway with only a few streetlamps. With adrenaline coursing through your veins, you "
        msg += "are quite exhausted. But, the mission isn't over until you make it home..."
        view = chips_bank_heist_rng_view(interaction, "d12", "73A", rolls = all_rolls, label = "Merge onto highway")

    return msg, view

def chips_bank_heist_stage_71A(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    view = discord.ui.View(timeout = None)
    rewards = chips_bank_heist_success()
    cost = 5 * all_rolls[4]
    rewards = int(rewards * cost / 100)
    msg += "You head towards the Thrift Store, hoping that they have a disguise. "
    if roll == 1:
        msg += "But, the door is locked. The sirens get louder and the lights get brighter. You turn around to see a swarm "
        msg += "of officers surrounding you and your car. You are immediately arrested, and your chips are seized. A jury "
        msg += "finds you guilty, and you are sent to prison.\n\n"
        msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
        color = 0xff0000
        chips_bank_heist_fail(interaction)
    elif roll < 7:
        msg += "You push open the door with ease, and immediately start searching around. Unfortunately, due to the high "
        msg += "crime in this area, the clothes section has been locked specifically to prevent people like yourself from "
        msg += "dressing in a disguise and fooling the cops. You can see red and blue lights flashing outside, and let "
        msg += "out a sigh of despair. As the cops flood the building, you turn yourself in.\n\n"
        msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
        color = 0xff0000
        chips_bank_heist_fail(interaction)
    else:
        msg += "As you walk into the shop, you locate the clothing section and start heading in that direction. You pick "
        msg += "out a crappy shirt, ripped jeans, and a wig for extra style points. As the sirens drear ever closer, "
        msg += "you rush to the changing room to put on your disguise. Cops flood the building, searching every nook and "
        msg += "cranny for the man who owns the car outside. An officer swipes the curtains to your changing room wide "
        msg += "open, and you decide to scream. Because you stuffed your old clothes up your shirt and put on a woman's "
        msg += "wig, you looked like a massive tranny to the policeman. He immediately apologizes and rounds everyone up "
        msg += "to leave...\n\n"
        msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Reward:** {rewards}x {DEAD_EMOJI} ({cost}% of possible)"
        msg += f"\n**Total Chips:** {give_chips(interaction.user, rewards)}x {DEAD_EMOJI}"
        color = 0x22cc22
    return msg, view, color

def chips_bank_heist_stage_71B(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    view = discord.ui.View(timeout = None)
    rewards = chips_bank_heist_success()
    cost = 5 * all_rolls[4]
    rewards = int(rewards * cost / 100)
    msg += "You head towards Castbrew Coffee, a beautiful coffee shop where you can play poker with the pals. "
    if roll == 1:
        msg += "But, the door is locked. The sirens get louder and the lights get brighter. You turn around to see a swarm "
        msg += "of officers surrounding you and your car. You are immediately arrested, and your chips are seized. A jury "
        msg += "finds you guilty, and you are sent to prison.\n\n"
        msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
        color = 0xff0000
        chips_bank_heist_fail(interaction)
    elif roll < 7:
        msg += "You push open the door with ease, and immediately start searching around. Unfortunately, due to your "
        msg += "suspicious demeanor, the owner of the kicks you out the door. "
        msg += "You can see red and blue lights flashing outside, and let "
        msg += "out a sigh of despair. As the cops flood the building, you turn yourself in.\n\n"
        msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
        color = 0xff0000
        chips_bank_heist_fail(interaction)
    else:
        msg += "As you walk into the shop, you locate the clothing section and start heading in that direction. You pick "
        msg += "out a crappy shirt, ripped jeans, and a wig for extra style points. As the sirens drear ever closer, "
        msg += "you rush to the changing room to put on your disguise. Cops flood the building, searching every nook and "
        msg += "cranny for the man who owns the car outside. An officer swipes the curtains to your changing room wide "
        msg += "open, and you decide to scream. Because you stuffed your old clothes up your shirt and put on a woman's "
        msg += "wig, you looked like a massive tranny to the policeman. He immediately apologizes and rounds everyone up "
        msg += "to leave...\n\n"
        msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Reward:** {rewards}x {DEAD_EMOJI} ({cost}% of possible)"
        msg += f"\n**Total Chips:** {give_chips(interaction.user, rewards)}x {DEAD_EMOJI}"
        color = 0x22cc22
    return msg, view, color

def chips_bank_heist_stage_71C(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    view = discord.ui.View(timeout = None)
    rewards = chips_bank_heist_success()
    cost = 5 * all_rolls[4]
    rewards = int(rewards * cost / 100)
    msg += "You head towards the fire stairs, hoping to make it all the way to the top. "
    if roll < 4:
        msg += "Unfortunately, the city is very poorly maintained and the fire stairs separate from the building and "
        msg += "collapses to the ground as soon as you reached the 5th floor. You are knocked out immediately. "
        msg += f"About {random.randint(2, 5)} days later, you wake up in a hospital bed, surrounded by police.\n\n"
        msg += "**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
        color = 0xff0000
        chips_bank_heist_fail(interaction)
    else:
        msg += "Fortunately, the cops start searching through the coffee shop and the thrift store before checking the "
        msg += f"fire stairs, leaving you ample time to reach the top of the {random.randint(6, 9)} story building. "
        msg += "Out of sight, you lie down, and let out a gasp of relief, knowing you are safe.\n\n"
        msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Reward:** {rewards}x {DEAD_EMOJI} ({cost}% of possible)"
        msg += f"\n**Total Chips:** {give_chips(interaction.user, rewards)}x {DEAD_EMOJI}"
        color = 0x22cc22

    return msg, view, color

def chips_bank_heist_stage_72A(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    view = discord.ui.View(timeout = None)
    rewards = chips_bank_heist_success()
    cost = 5 * all_rolls[4]
    msg += "As you head towards the construction site on the bridge, you decide to use a ramp to jump over the swarm of "
    msg += "police. You line up the car, close your eyes, and hold on to your butt as the car flies into the air. "
    if roll < 3:
        msg += "With a massive crash as you hit the road, you open your eyes to see all the cops behind you. Relieved, "
        msg += "you feel around in the passenger seat for the bag of chips, but find nothing. A bit worried now, you look "
        msg += "over into the rear seats to find nothing, and then look up at the sunroof, which was open the entire time."
        msg += f"\n\n**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success??\n**Reward:** 0x {DEAD_EMOJI} "
        msg += f"(note to self: close the sunroof)\n**Total Chips:** {give_chips(interaction.user, 0)}x {DEAD_EMOJI}"
        color = 0x00ff88
    else:
        msg += "After crashing against the ground and spinning out, you look out of the windshield in a daze to see. "
        msg += "all the cops in front of you. Relieved, you feel around in the passenger seat for the bag of chips, but "
        msg += "it feels a bit empty. Unfortunately, because you forgot to zip the bag, "
        extra_cost = (roll + 2) / 16
        msg += f"about {int(extra_cost * 100)}% of the chips inside flew out of the open window...\n\n"
        cost = int(cost * (1 - extra_cost))
        rewards = int(rewards * cost / 100)
        msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Reward:** {rewards}x {DEAD_EMOJI} ({cost}% of possible)"
        msg += f"\n**Total Chips:** {give_chips(interaction.user, rewards)}x {DEAD_EMOJI}"
        color = 0x22cc22

    return msg, view, color

def chips_bank_heist_stage_72B(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    view = discord.ui.View(timeout = None)
    rewards = chips_bank_heist_success()
    cost = 5 * all_rolls[4]
    msg += "As you head towards the construction site on the bridge, you decide to swerve right into the wall and flip "
    msg += "the car over into the river. The car starts to fill with water, and you are in a hurry to get out. You open "
    msg += "the door, grab hold of the bag, and try to swim out. "
    if roll < 3:
        msg += "Unfortunately, the other strap was caught around the headrest of the seat. As the car sinks lower, and you "
        msg += "run out of breath, you decide to abandon ship and make to the surface. The cops look down into the dark  "
        msg += "river, and are unable to spot you, so you swim to shore.\n\n"
        msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success??\n**Reward:** 0x {DEAD_EMOJI} "
        msg += f"(note to self: close the sunroof)\n**Total Chips:** {give_chips(interaction.user, 0)}x {DEAD_EMOJI}"
        color = 0x00ff88
    else:
        msg += "Quickly, you swim to the surface to regain your breath, and soon start swimming to shore. Once you crawl "
        msg += "out and slap the bag against the sand, you realize that there is a massive hole. Unfortunately, the "
        msg += "impact with the bridge wall was so violent that the bag of chips burst open, causing "
        extra_cost = (roll + 2) / 12
        msg += f"about {int(extra_cost * 100)}% of the chips stay inside the sinking car...\n\n"
        cost = int(cost * (1 - extra_cost))
        rewards = int(rewards * cost / 100)
        msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Reward:** {rewards}x {DEAD_EMOJI} ({cost}% of possible)"
        msg += f"\n**Total Chips:** {give_chips(interaction.user, rewards)}x {DEAD_EMOJI}"
        color = 0x22cc22

    return msg, view, color

def chips_bank_heist_stage_73A(interaction):
    msg, roll, all_rolls = chips_bank_heist_get_rolls(interaction)
    view = discord.ui.View(timeout = None)
    rewards = chips_bank_heist_success()
    cost = 5 * all_rolls[4]
    msg += "You take a few side roads before merging on to the highway. "
    if roll < 11:
        msg += "Unfortunately, you were quite predictable in your 'random' movements, meaning the cops gained on you "
        msg += "quite quickly. "
        if all_rolls[5] < 13:
            msg += "Even worse, all that time you spend fumbling around unable to open the door or locate your keys "
            msg += "allowed the cops to follow you even closer, allowing them to try at a pit maneuver. "
            msg += f"They made {random.randint(3, 12)} attempts before finally landing one. "
            if roll == 1:
                msg += "And this one was devastating, causing you to spin out completely and crash into a "
                msg += random.choice(["tree", "lamp post", "ditch", "concrete divider"]) + " and black out immediately. "
                msg += "Hours later, you wake up in a daze, "
                msg += random.choice([
                    "with your head in a metal toilet.",
                    "facing a concrete wall.",
                    "laying against a white padded wall in an empty room.",
                    "wearing a bright orange jump suit."
                ])
                msg += "\n\n**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Failure\n**Penalty:** Chips seized for 24 hours"
                color = 0xff0000
                chips_bank_heist_fail(interaction)
            else:
                extra_cost = 2 * roll
                msg += "You do a complete 180 and recover quickly. You look in the rearview mirror and laugh hysterically "
                msg += "as the officer that did the pit maneuver crashed into the others, causing a complete road block, "
                msg += f"and stacking upwards of {random.choice([15, 25, 50])} police cars. Looking over at the passenger "
                msg += f"seat, you find chips all strewn about the floor, and about {extra_cost}% flew out of the window, "
                msg += "thanks to the violent maneuver.\n\n"
                cost = int(cost * (1 - extra_cost / 100))
                rewards = int(rewards * cost / 100)
                msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Reward:** {rewards}x {DEAD_EMOJI} ({cost}% of possible)"
                msg += f"\n**Total Chips:** {give_chips(interaction.user, rewards)}x {DEAD_EMOJI}"
                color = 0x22cc22
        else:
            msg += "But, thanks to a well timed U-turn as you drove past an exit, and a subsequent merge on to a different "
            msg += "highway, you were able to lose them, and in style.\n\n"
            rewards = int(rewards * cost / 100)
            msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Reward:** {rewards}x {DEAD_EMOJI} ({cost}% of possible)"
            msg += f"\n**Total Chips:** {give_chips(interaction.user, rewards)}x {DEAD_EMOJI}"
            color = 0x22cc22
    else:
        msg += "But thanks to your erratic driving, swerving and overall unpredictability, you lost the cops miles back.\n\n"
        rewards = int(rewards * cost / 100)
        msg += f"**-~=:[ MISSION SUMMARY ]:=~-**\n**Result:** Success\n**Reward:** {rewards}x {DEAD_EMOJI} ({cost}% of possible)"
        msg += f"\n**Total Chips:** {give_chips(interaction.user, rewards)}x {DEAD_EMOJI}"
        color = 0x22cc22

    return msg, view, color

async def get_chips_rob_bank(interaction: discord.Interaction, stage):
    heist_meme = False
    color = 0xffaa44

    match stage:
        case "0":
            msg, view = chips_bank_heist_stage_0(interaction)
        case "1":
            msg, view = chips_bank_heist_stage_1(interaction)
        case "2":
            msg, view = chips_bank_heist_stage_2(interaction)
        case "3":
            msg, view = chips_bank_heist_stage_3(interaction)
        case "3FA":
            msg, view, color = chips_bank_heist_stage_3FA(interaction)
        case "3FB":
            msg, view, color, heist_meme = chips_bank_heist_stage_3FB(interaction)
        case "4":
            msg, view = chips_bank_heist_stage_4(interaction)
        case "4S":
            msg, view, color = chips_bank_heist_stage_4S(interaction)
        case "5":
            msg, view = chips_bank_heist_stage_5(interaction)
        case "6":
            msg, view = chips_bank_heist_stage_6(interaction)
        case "7":
            msg, view = chips_bank_heist_stage_7(interaction)
        case "71A":
            msg, view, color = chips_bank_heist_stage_71A(interaction)
        case "71B":
            msg, view, color = chips_bank_heist_stage_71B(interaction)
        case "71C":
            msg, view, color = chips_bank_heist_stage_71C(interaction)
        case "72A":
            msg, view, color = chips_bank_heist_stage_72A(interaction)
        case "72B":
            msg, view, color = chips_bank_heist_stage_72B(interaction)
        case "73A":
            msg, view, color = chips_bank_heist_stage_73A(interaction)

    embed = discord.Embed(
        title = "Attempt at a bank heist",
        description = msg,
        color = color
    )
    embed.set_footer(text = "Definitely less legal by West Virginia law...")

    if stage == "0":
        return await interaction.response.send_message(embed = embed, view = view, ephemeral = interaction.channel.id not in BOT_CHANNELS)

    await interaction.response.edit_message(embed = embed, view = view)
    if heist_meme:
        await interaction.followup.send(file = discord.File(open(ROOT_DATA + "HeistTraining.webm", "rb")))
