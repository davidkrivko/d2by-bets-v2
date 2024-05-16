from sqlalchemy import select, and_, or_, update
from sqlalchemy.dialects.postgresql import insert
from database.tables import Match, BetsHistory
from bets4pro.tables import Bets4ProBets, Bets4ProMatches
from d2by.tables import D2BYBets, D2BYMatches
from database.connection import async_session
from fan_sport.tables import FanSportBets


async def get_bets():
    async with async_session() as session:
        stmt = (
            select(
                Match.id,
                Match.team_1,
                Match.team_2,
                Match.start_at,
                Bets4ProBets.cfs,
                D2BYBets.cfs,
                FanSportBets.cfs,
                Bets4ProBets.id,
                D2BYBets.id,
                FanSportBets.id,
                Bets4ProBets.value,
                Bets4ProBets.side,
                Bets4ProBets.map,
                Bets4ProBets.type_id,
                D2BYBets.probs,
                D2BYBets.d2by_id,
                D2BYBets.is_shown,
                D2BYMatches.url,
                Bets4ProBets.bets4pro_name,
                Bets4ProBets.is_shown,
                Bets4ProBets.match_start_at,
                Bets4ProMatches.url,
                Bets4ProMatches.bets4pro_id,
                Bets4ProMatches.is_reverse,
            )
            .join(Bets4ProBets, Match.id == Bets4ProBets.match_id)
            .outerjoin(D2BYMatches, Match.id == D2BYMatches.match_id)
            .outerjoin(Bets4ProMatches, Match.id == Bets4ProMatches.match_id)
            .outerjoin(
                D2BYBets,
                and_(
                    or_(Bets4ProBets.map == D2BYBets.map, and_(Bets4ProBets.map == None, D2BYBets.map == None)),
                    or_(Bets4ProBets.side == D2BYBets.side, and_(Bets4ProBets.side == None, D2BYBets.side == None)),
                    or_(Bets4ProBets.value == D2BYBets.value,
                        and_(Bets4ProBets.value == None, D2BYBets.value == None)),
                    Bets4ProBets.type_id == D2BYBets.type_id,
                    Bets4ProBets.match_id == D2BYBets.match_id,
                    D2BYBets.is_active == True,
                )
            )
            .outerjoin(
                FanSportBets,
                and_(
                    or_(Bets4ProBets.map == FanSportBets.map,
                        and_(Bets4ProBets.map == None, FanSportBets.map == None)),
                    or_(Bets4ProBets.side == FanSportBets.side,
                        and_(Bets4ProBets.side == None, FanSportBets.side == None)),
                    or_(Bets4ProBets.value == FanSportBets.value,
                        and_(Bets4ProBets.value == None, FanSportBets.value == None)),
                    Bets4ProBets.type_id == FanSportBets.type_id,
                    # FanSportBets.is_active == True,
                    Bets4ProBets.match_id == FanSportBets.match_id,
                )
            )
            .filter(
                and_(
                    or_(D2BYBets.cfs != None, FanSportBets.cfs != None),
                    Bets4ProBets.is_active == True,
                )
            )
        )

        result = await session.execute(stmt)
        return result.fetchall()


async def is_shown_true(ids, table):
    async with async_session() as session:
        stmt = update(table).where(table.id.in_(ids)).values(is_shown=True)

        await session.execute(stmt)
        await session.commit()


async def is_shown_false(table):
    async with async_session() as session:
        stmt = update(table).where(True).values(is_shown=False)

        await session.execute(stmt)
        await session.commit()


async def save_history(data: list):
    async with async_session() as session:
        try:
            stmt = insert(BetsHistory).values(data)
            on_conflict_stmt = stmt.on_conflict_do_update(
                constraint='bets_history_unique_constrain',
                set_={k.name: getattr(stmt.excluded, k.name) for k in BetsHistory.__table__.columns if k.name != 'id'}
            )
            await session.execute(on_conflict_stmt)
            await session.commit()
        except Exception as e:
            print(e)
