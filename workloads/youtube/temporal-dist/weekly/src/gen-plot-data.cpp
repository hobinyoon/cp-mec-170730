#include <fstream>
#include <map>
#include <typeinfo>
#include <vector>

#include <boost/date_time/gregorian/gregorian.hpp>
#include <boost/filesystem.hpp>

#include "conf.h"
#include "cons.h"
#include "gen-plot-data.h"
#include "stat.h"
#include "youtube-data.h"

using namespace std;

namespace GenPlotData {

  void Run() {
    YoutubeData::Load();

    //Cons::MT _(boost::format("Loading YouTube workload from file %s ...") % fn);

    // To reduce the number of boost calls, we bin by date first
    // map<date, cnt>
    map<string, int> date_cnt;
    for (auto op: YoutubeData::Entries()) {
      const string& date0 = op->created_at.substr(0, 10);
      auto it = date_cnt.find(date0);
      if (it == date_cnt.end()) {
        date_cnt[date0] = 1;
      } else {
        it->second ++;
      }
    }

    const std::locale fmt0(std::locale::classic(), new boost::gregorian::date_input_facet("%Y-%m-%d"));
    map<boost::gregorian::greg_weekday, vector<int> > dow_cnt;
    for (auto i: date_cnt) {
      const auto& date0 = i.first;
      std::istringstream is(date0);
      is.imbue(fmt0);
      boost::gregorian::date date1;
      is >> date1;

      auto dow = date1.day_of_week();
      auto it = dow_cnt.find(dow);
      if (it == dow_cnt.end()) {
        dow_cnt[dow] = vector<int>();
      }
      dow_cnt[dow].push_back(i.second);
    }

    for (auto i: dow_cnt) {
      auto dow = i.first;
      auto cnts = i.second;

      Stat::Result<int> r = Stat::Gen<int>(cnts);
      Cons::P(boost::format("%s %.2f %4f %4f %4f %4f %4f") % dow % r.avg % r.min % r._25p % r._50p % r._75p % r.max);
    }

    //N5boost9gregorian12greg_weekdayE
    //cout << typeid(date1.day_of_week()).name() << '\n';

    exit(1);

//    const string& fn = Conf::fn_plot_data;
//    ofstream ofs(fn);
//    ofs << "# date cnt\n";
//    for (auto i: date_cnt)
//      ofs << boost::format("%s %d\n") % i.first % i.second;
//    ofs.close();
//    Cons::P(boost::format("Created %s %d") % fn % boost::filesystem::file_size(fn));
  }

};
