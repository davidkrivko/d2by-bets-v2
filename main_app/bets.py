from sqlalchemy import select, and_, or_
from database.tables import Match
from bets4pro.tables import Bets4ProBets
from d2by.tables import D2BYBets
from database.connection import async_session
from fan_sport.tables import FanSportBets


async def get_bets():
    async with async_session() as session:
        stmt = (
            select(
                Match.id,
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
            )
            .join(Bets4ProBets, Match.id == Bets4ProBets.match_id)
            .outerjoin(
                D2BYBets,
                and_(
                    or_(Bets4ProBets.map == D2BYBets.map, and_(Bets4ProBets.map == None, D2BYBets.map == None)),
                    or_(Bets4ProBets.side == D2BYBets.side, and_(Bets4ProBets.side == None, D2BYBets.side == None)),
                    or_(Bets4ProBets.value == D2BYBets.value,
                        and_(Bets4ProBets.value == None, D2BYBets.value == None)),
                    Bets4ProBets.type_id == D2BYBets.type_id,
                    D2BYBets.is_active == True,
                    Bets4ProBets.match_id == D2BYBets.match_id
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
                    FanSportBets.is_active == True,
                    Bets4ProBets.match_id == FanSportBets.match_id
                )
            )
            .filter(
                and_(
                    or_(D2BYBets.cfs != None, FanSportBets.cfs != None),
                    Bets4ProBets.is_active == True,
                    Bets4ProBets.is_live == True,
                )
            )
        )

        result = await session.execute(stmt)
        return result.fetchall()
