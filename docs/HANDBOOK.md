# isabot official handbook!

## Abstract

This handbook contains the relevant information on the leaderboard system for Isabot. Join the AR Club Discord server and guild on Bronzebeard-Shandris to join in on the fun.

## Privacy

Isabot stores the following information upon a successful sign-in:

1. WoW characters that are in Bronzebeard-Shandris *and* the AR Club guild. Specifically, the character name, id, and realm name, slug name, and id. 
2. Your account battle tags *without* the unique identifier.
3. Number of mounts in account-wide collection

Your WoW characters are used to update the fields you are competing in (i.e mounts, etc). 

## Leaderboard

The leaderboard is composed of leaderboard entries. Each entry contains the players that signed up for the leaderboard and the fields they are competing in, such as
the highest amount of mounts, etc (more fields will come soon). An entry is created and sent to the Discord server every Sunday at 20:00 UTC. To ensure that each field for each player is accurate, the system updates your data in the database weekly using the characters given.


## Discord Slash Commands

### `/lb cmd latest`

Gets the latest leaderboard entry. 

## Website Pages 

### `/lb`

Gets all leaderboard entries. 

### `/lb/latest`

Gets the latest leaderboard entry. 

### `/signin`

Sign in with Isabot using your Battle.net account.

### `/signout`

Sign out of Isabot.

### `/invite`

Invites Isabot to your Discord server.

## Current Limitations

The only way to update your list of characters with Isabot is to sign in again with your Battle.net account. Due to the limitations of the Blizzard API, there is no way to 
update data automatically. 
