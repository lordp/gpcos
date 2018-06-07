from standings.models import Driver, Result, Race, Team, SeasonStats, Season
from standings_api.serializers import DriverSerializer, ResultSerializer, RaceSerializer, TeamSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins, generics
from datetime import datetime, timezone
from django.db.models import Q
from django.forms.models import model_to_dict


class DriverList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Driver.objects.all().order_by('name')
    serializer_class = DriverSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ResultList(generics.ListAPIView):
    serializer_class = ResultSerializer

    def get_queryset(self):
        queryset = Result.objects.all()

        driver_name = self.request.query_params.get('name', None)
        if driver_name is not None:
            queryset = queryset.filter(driver__name__icontains=driver_name)

        season = self.request.query_params.get('season', None)
        if season is not None:
            queryset = queryset.filter(race__season__id=season)

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class DriverDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class TeamDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class RaceDetail(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class NextRaceDetail(APIView):
    @staticmethod
    def get(request):
        now = datetime.now(timezone.utc)
        queryset = Race.objects.filter(start_time__gte=now).order_by('start_time')
        search = request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(
                season__division__league__name__iexact=search.lower()
            ) | Q(
                season__division__name__iexact=search.lower()
            ))

        race = model_to_dict(queryset.first())

        return Response(race)


class DriverStats(APIView):
    @staticmethod
    def get(request):
        stats = SeasonStats.objects
        driver = request.query_params.get('driver', None)
        if driver:
            stats = stats.filter(driver__name__icontains=driver)

        season = request.query_params.get('season', None)
        if season:
            stats = stats.filter(season__name__icontains=season)

        division = request.query_params.get('division', None)
        if division:
            stats = stats.filter(season__division__name__icontains=division)

        try:
            if len(stats) > 0:
                driver_id = 0
                addable_stats = [
                    "fastest_laps",
                    "laps_completed",
                    "laps_lead",
                    "podiums",
                    "points_finishes",
                    "pole_positions",
                    "wins",
                    "attendance"
                ]

                driver_stats = {
                    "best_finish": 99,
                    "fastest_laps": 0,
                    "laps_completed": 0,
                    "laps_lead": 0,
                    "podiums": 0,
                    "points_finishes": 0,
                    "pole_positions": 0,
                    "wins": 0,
                    "attendance": 0
                }

                for stat in stats:
                    if driver_id == 0:
                        driver_id = stat.driver.id
                        driver_stats['name'] = stat.driver.name
                    elif driver_id != stat.driver.id:
                        continue

                    for key in driver_stats:
                        if key == 'best_finish' and getattr(stat, key, 0) < driver_stats['best_finish']:
                            driver_stats[key] = getattr(stat, key, 0)
                        elif key in addable_stats:
                            driver_stats[key] += getattr(stat, key, 0)

                return Response(driver_stats)
        except TypeError:
            return Response({}, status=404)


class Standings(APIView):
    @staticmethod
    def get(request, season_id, team):
        season = Season.objects.get(pk=season_id)
        if season:
            data = []
            standings = season.get_standings()
            if team:
                standings = standings[1]
            else:
                standings = standings[0]

            for row in standings:
                if team:
                    data.append({
                        'name': row['team'].name,
                        'position': row['position'],
                        'points': row['points'],
                    })
                else:
                    data.append({
                        'name': row['driver'].name,
                        'position': row['position'],
                        'points': row['points'],
                        'best_finish': row['best_finish']
                    })
            return Response(data)
        else:
            return Response({}, status=404)
