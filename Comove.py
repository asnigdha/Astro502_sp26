# import pkg_resources
##figure out where the big fits files are in this installation
datapath = './resources' #pkg_resources.resource_filename('Comove','resources')
import math as math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import astropy.units as u
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad

Simbad.reset_votable_fields()
Simbad.TIMEOUT = 1500
Simbad.server = "simbad.harvard.edu"
#Simbad.add_votable_fields('typed_id')
customSimbad = Simbad()
customSimbad.add_votable_fields('rvz_radvel','rvz_err','rvz_bibcode')
from astropy.coordinates import SkyCoord
from astropy import coordinates
from astropy.coordinates import ICRS
from astroquery.gaia import Gaia
from astroquery.exceptions import NoResultsWarning
import galpy.util.coords as bc
import matplotlib.pyplot as plt
from matplotlib import cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.ticker as mticker
from astroquery.mast import Catalogs
from astroquery.ipac.irsa import Irsa
Irsa.TIMEOUT = 600
from astropy.coordinates import SkyCoord
from scipy.interpolate import interp1d
from scipy.io import readsav
from astroquery.vizier import Vizier
from astropy.utils.data import conf
conf.remote_timeout = 60.0
Vizier.TIMEOUT = 600
import os,warnings,sys
import urllib.request
import csv
import pickle
import matplotlib as mpl

#if 'dustmaps.bayestar' in sys.modules: print('Bayestar already imported, skipping 30-second load time.')

"""
if 'dustmaps.bayestar' not in sys.modules:
    print('Bayestar not imported, doing so now. Will require 30 seconds or so.')
    from dustmaps.config import config
    datadir = '~/Dropbox/Malmquist/'
    bayestarver = 'bayestar2019'
    testname = datadir + 'bayestar/' + bayestarver + '.h5'
    config['data_dir'] = datadir
    from dustmaps.bayestar import BayestarQuery
    bayestar = BayestarQuery(version=bayestarver)
    if ((os.path.isfile(os.path.expanduser(testname))) == True) : print('Already downloaded Bayestar files.')
    if ((os.path.isfile(os.path.expanduser(testname))) == False):
        import dustmaps.bayestar # Only uncomment if running in a new place to download dust maps again
        dustmaps.bayestar.fetch()
"""

mpl.rcParams['lines.linewidth']   = 2
mpl.rcParams['axes.linewidth']    = 2
mpl.rcParams['xtick.major.width'] =2
mpl.rcParams['ytick.major.width'] =2
mpl.rcParams['ytick.labelsize'] = 10
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['axes.labelsize'] = 14
mpl.rcParams['legend.numpoints'] = 1
mpl.rcParams['axes.labelweight']='semibold'
mpl.rcParams['axes.titlesize']=9
mpl.rcParams['axes.titleweight']='semibold'
mpl.rcParams['font.weight'] = 'semibold'
plt.rcParams['figure.facecolor'] = 'white'

def findfriends(targname, radial_velocity, velocity_limit=5.0, search_radius=25.0,
                rvcut=5.0, convergcut=5.0, radec=[None, None],
                output_directory=None, showplots=False, verbose=False,
                DoGALEX=False, DoWISE=False, DoROSAT=False):

    radvel = radial_velocity * u.kilometer / u.second
    if (convergcut is None): convergcut = 0.0

    # ---------- Output directory ----------
    if output_directory is None:
        outdir = './' + targname.replace(" ", "") + '_friends/'
    else:
        outdir = output_directory

    if os.path.isdir(outdir):
        print('Output directory ' + outdir + ' Already Exists!!')
        print('Either Move it, Delete it, or input a different [output_directory] Please!')
        return
    os.mkdir(outdir)

    if velocity_limit < 1e-5:
        print('input velocity_limit is too small, try something else')
        print('velocity_limit: ' + str(velocity_limit))
    if search_radius < 1e-7:
        print('input search_radius is too small, try something else')
        print('search_radius: ' + str(search_radius))

    vlim = velocity_limit * u.kilometer / u.second
    searchradpc = search_radius * u.parsec

    # ---------- Resolve coordinates ----------
    if (radec[0] is not None) and (radec[1] is not None):
        usera, usedec = radec[0], radec[1]
    else:
        print('Asking Simbad for RA and DEC')
        result_table = Simbad.query_object(targname)
        usera, usedec = result_table['ra'][0], result_table['dec'][0]

    if verbose:
        print('Target name: ', targname)
        print('Coordinates: ' + str(usera) + ' ' + str(usedec))
        print()

    c = SkyCoord(ra=usera, dec=usedec, unit=(u.deg, u.deg), frame='icrs')
    if verbose: print(c)

    # ---------- Gaia: precise target ----------
    print('Asking Gaia for precise coordinates')
    sqltext = f"""
    SELECT *
    FROM gaiadr3.gaia_source
    WHERE CONTAINS(
        POINT('ICRS', gaiadr3.gaia_source.ra, gaiadr3.gaia_source.dec),
        CIRCLE('ICRS', {c.ra.value}, {c.dec.value}, {6.0/3600.0})
    )=1
    """
    job = Gaia.launch_job_async(sqltext, dump_to_file=False)
    Pgaia = job.get_results()
    job = Gaia.launch_job_async(sqltext, dump_to_file=False)
    Pgaia = job.get_results()

    if len(Pgaia) == 0:
        print("DEBUG: Gaia target cone search returned 0 rows. Writing empty outputs.")
        # Write an empty header-only file
        filename = outdir + targname.replace(" ", "") + ".txt"
        with open(filename, 'w') as f:
            f.write("GaiaDR3 RA DEC Gmag Bp-Rp Voff(km/s) Sep(deg) 3D(pc) Vr(pred) Vr(obs) Vrerr Plx(mas) SpT FnuvJ W1-W3 RUWE XCrate RVsrc PMRApred PMDecpred PMRA PMRAerr PMDec PMDecerr\n")
        # Convert to csv
        csv_filename = outdir + targname.replace(" ", "") + ".csv"
        original_headers = pd.read_csv(filename, sep=r'\s+', nrows=0).columns.tolist()
        new_names = ['Catalog', 'Type'] + original_headers
        csv_file = pd.read_csv(filename, sep=r'\s+', names=new_names, skiprows=1, index_col=False)
        csv_file.to_csv(csv_filename, index=False)
        return outdir

    # pick brightest unmasked
    minpos = Pgaia['phot_g_mean_mag'].tolist().index(
        min(Pgaia['phot_g_mean_mag'][~Pgaia['phot_g_mean_mag'].mask])
    )

    Pcoord = SkyCoord(
        ra=Pgaia['ra'][minpos]*u.deg,
        dec=Pgaia['dec'][minpos]*u.deg,
        distance=(1000.0/Pgaia['parallax'][minpos])*u.parsec,
        frame='icrs',
        radial_velocity=radvel,
        pm_ra_cosdec=Pgaia['pmra'][minpos]*u.mas/u.year,
        pm_dec=Pgaia['pmdec'][minpos]*u.mas/u.year
    )

    searchraddeg = np.arcsin(searchradpc / Pcoord.distance).to(u.deg)
    minpar = (1000.0*u.parsec) / (Pcoord.distance + searchradpc) * u.mas

    if verbose:
        print(Pcoord)
        print('Search radius in deg: ', searchraddeg)
        print('Minimum parallax: ', minpar)

    # ---------- Gaia: neighbor query ----------
    print('Querying Gaia for neighbors')
    Pllbb = bc.radec_to_lb(Pcoord.ra.value, Pcoord.dec.value, degree=True)
    if np.abs(Pllbb[1]) > 10.0:
        plxcut = max(0.5, (1000.0 / Pcoord.distance.value / 10.0))
    else:
        plxcut = 0.5
    print('Parallax cut: ', plxcut)

    # Build neighbor query safely (avoids broken quote bugs)
    if (searchradpc < Pcoord.distance):
        sqltext = f"""
        SELECT *
        FROM gaiadr3.gaia_source
        WHERE CONTAINS(
            POINT('ICRS', gaiadr3.gaia_source.ra, gaiadr3.gaia_source.dec),
            CIRCLE('ICRS', {Pcoord.ra.value}, {Pcoord.dec.value}, {searchraddeg.value})
        ) = 1
        AND parallax > {minpar.value}
        AND parallax_error < {plxcut};
        """
    else:
        sqltext = f"""
        SELECT *
        FROM gaiadr3.gaia_source
        WHERE parallax > {minpar.value}
        AND parallax_error < {plxcut};
        """
        print('Note, using all-sky search')

    if verbose:
        print(sqltext)
        print()

    job = Gaia.launch_job_async(sqltext, dump_to_file=False)
    r = job.get_results()

    if len(r) == 0:
        print("DEBUG: Gaia neighbor query returned 0 rows. Writing empty outputs.")
        filename = outdir + targname.replace(" ", "") + ".txt"
        with open(filename, 'w') as f:
            f.write("GaiaDR3 RA DEC Gmag Bp-Rp Voff(km/s) Sep(deg) 3D(pc) Vr(pred) Vr(obs) Vrerr Plx(mas) SpT FnuvJ W1-W3 RUWE XCrate RVsrc PMRApred PMDecpred PMRA PMRAerr PMDec PMDecerr\n")
        csv_filename = outdir + targname.replace(" ", "") + ".csv"
        original_headers = pd.read_csv(filename, sep=r'\s+', nrows=0).columns.tolist()
        new_names = ['Catalog', 'Type'] + original_headers
        csv_file = pd.read_csv(filename, sep=r'\s+', names=new_names, skiprows=1, index_col=False)
        csv_file.to_csv(csv_filename, index=False)
        return outdir

    if verbose: print('Number of records: ', len(r))

    # ---------- Build coordinate arrays ----------
    gaiacoord = SkyCoord(
        ra=r['ra'],
        dec=r['dec'],
        distance=(1000.0/r['parallax'])*u.parsec,
        frame='icrs',
        pm_ra_cosdec=r['pmra'],
        pm_dec=r['pmdec']
    )

    sep = gaiacoord.separation(Pcoord)
    sep3d = gaiacoord.separation_3d(Pcoord)

    # ---------- Convergent point + predicted PM ----------
    Pllbb = bc.radec_to_lb(Pcoord.ra.value, Pcoord.dec.value, degree=True)
    Ppmllpmbb = bc.pmrapmdec_to_pmllpmbb(
        Pcoord.pm_ra_cosdec.value, Pcoord.pm_dec.value,
        Pcoord.ra.value, Pcoord.dec.value, degree=True
    )
    Pvxvyvz = bc.vrpmllpmbb_to_vxvyvz(
        Pcoord.radial_velocity.value, Ppmllpmbb[0], Ppmllpmbb[1],
        Pllbb[0], Pllbb[1], Pcoord.distance.value/1000.0,
        XYZ=False, degree=True
    )

    Cll = (math.atan2(Pvxvyvz[1], Pvxvyvz[0]) * 180.0/np.pi) % 360
    Cbb = math.atan2(Pvxvyvz[2], np.sqrt(Pvxvyvz[0]**2 + Pvxvyvz[1]**2)) * 180.0/np.pi
    Cradec = bc.lb_to_radec(Cll, Cbb, degree=True, epoch=2000.0)
    Ccoord = SkyCoord(ra=Cradec[0]*u.deg, dec=Cradec[1]*u.deg, distance=999999.9, frame='icrs')

    Cangle = gaiacoord.separation(Ccoord)
    zzflip = np.where((Cangle.degree > 90.0))
    if np.array(zzflip).size > 0:
        Cangle[zzflip] = (180.0 - Cangle[zzflip].degree)*u.deg

    Gllbb = bc.radec_to_lb(gaiacoord.ra.value, gaiacoord.dec.value, degree=True)
    Gxyz = bc.lbd_to_XYZ(Gllbb[:, 0], Gllbb[:, 1], gaiacoord.distance/1000.0, degree=True)
    Gvrpmllpmbb = bc.vxvyvz_to_vrpmllpmbb(
        Pvxvyvz[0]*np.ones(len(Gxyz[:, 0])),
        Pvxvyvz[1]*np.ones(len(Gxyz[:, 1])),
        Pvxvyvz[2]*np.ones(len(Gxyz[:, 2])),
        Gxyz[:, 0], Gxyz[:, 1], Gxyz[:, 2], XYZ=True
    )
    Gpmrapmdec = bc.pmllpmbb_to_pmrapmdec(
        Gvrpmllpmbb[:, 1], Gvrpmllpmbb[:, 2],
        Gllbb[:, 0], Gllbb[:, 1], degree=True
    )

    # predicted PM error model
    Gvtanerr = 1.0 * np.ones(len(Gxyz[:, 0]))
    Gpmerr = Gvtanerr * 206265000.0 * 3.154e7 / (gaiacoord.distance.value * 3.086e13)

    Gchi2 = np.sqrt(
        (Gpmrapmdec[:, 0] - gaiacoord.pm_ra_cosdec.value)**2 +
        (Gpmrapmdec[:, 1] - gaiacoord.pm_dec.value)**2
    ) / Gpmerr

    # ---------- RV arrays always exist ----------
    RV = np.full(np.array(r['ra']).size, np.nan, dtype=float)
    RVerr = np.full(np.array(r['ra']).size, np.nan, dtype=float)
    RVsrc = np.array(['                             None' for _ in range(np.array(r['ra']).size)])

    # candidates for RV population
    cand = np.where((sep3d.value < searchradpc.value) & (Gchi2 < vlim.value))[0]
    cand = cand[np.argsort(sep3d[cand])] if cand.size > 0 else cand

    print('Populating RV table')
    for idx in cand:
        if np.isnan(r['radial_velocity'][idx]) == False:
            RV[idx] = r['radial_velocity'][idx]
            if (np.ma.is_masked(r['teff_gspphot'][idx]) == False):
                if (r['teff_gspphot'][idx] >= 8500.0) and (np.ma.is_masked(r['grvs_mag'][idx]) == False):
                    RV[idx] = r['radial_velocity'][idx] - (7.98 - 1.135 * r['grvs_mag'][idx])
                elif (r['teff_gspphot'][idx] >= 8500.0) and (np.ma.is_masked(r['phot_rp_mean_mag'][idx]) == False):
                    RV[idx] = r['radial_velocity'][idx] - (7.98 - 1.135 * r['phot_rp_mean_mag'][idx])
            RVerr[idx] = r['radial_velocity_error'][idx]
            RVsrc[idx] = 'Gaia_DR3'

    if os.path.isfile('LocalRV.csv'):
        with open('LocalRV.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            next(readCSV)
            for row in readCSV:
                ww = np.where(r['designation'] == row[0])[0]
                if (np.array(ww).size == 1) and (RVerr[ww] > float(row[3])):
                    RV[ww] = float(row[2])
                    RVerr[ww] = float(row[3])
                    RVsrc[ww] = row[4]

    # ---------- Defaults for outputs used later ----------
    sptstring = ["nan" for _ in range(np.array(r['bp_rp']).size)]
    fnuvj = np.full(np.array(r['ra']).size, np.nan, dtype=float)
    W13 = np.full(np.array(r['ra']).size, np.nan, dtype=float)
    W13err = np.full(np.array(r['ra']).size, np.nan, dtype=float)
    ROSATflux = np.full(np.array(r['ra']).size, np.nan, dtype=float)

    # ---------- Plot helpers ----------
    def _save_or_skip(fig, fname):
        try:
            plt.savefig(fname, bbox_inches='tight', pad_inches=0.2, dpi=200)
            if showplots: plt.show()
        finally:
            plt.close('all')

    # ---------- CMD plot ----------
    try:
        mamajek = np.loadtxt(datapath + '/sptGBpRp.txt')
        pleiades = np.loadtxt(datapath + '/PleGBpRp.txt')
        tuchor = np.loadtxt(datapath + '/TucGBpRp.txt')
        usco = np.loadtxt(datapath + '/UScGBpRp.txt')
        chai = np.loadtxt(datapath + '/ChaGBpRp.txt')

        zz = np.where((sep3d.value < searchradpc.value) & (Gchi2 < vlim.value) & (np.isnan(r['bp_rp']) == False))[0]
        yy = zz[np.argsort(sep3d[zz])] if zz.size > 0 else np.array([], dtype=int)

        zz2 = np.where((sep3d.value < searchradpc.value) & (Gchi2 < vlim.value) &
                       (sep.degree > 1e-5) &
                       (r['phot_bp_rp_excess_factor'] < (1.3 + 0.06*r['bp_rp']**2)) &
                       (Cangle.degree > convergcut) &
                       (np.isnan(r['bp_rp']) == False))[0]
        yy2 = zz2[np.argsort((-Gchi2)[zz2])] if zz2.size > 0 else np.array([], dtype=int)

        if yy.size == 0 or yy2.size == 0:
            print("DEBUG: CMD selection empty; skipping CMD plot.")
        else:
            figname = outdir + targname.replace(" ", "") + "cmd.png"
            fig, ax1 = plt.subplots(figsize=(12, 8))
            ccc = None
            ddd = None

            ax1.axis([
                math.floor(min(r['bp_rp'][zz])),
                math.ceil(max(r['bp_rp'][zz])),
                math.ceil(max((r['phot_g_mean_mag'][zz] - (5.0*np.log10(gaiacoord.distance[zz].value)-5.0)))) + 1,
                math.floor(min((r['phot_g_mean_mag'][zz] - (5.0*np.log10(gaiacoord.distance[zz].value)-5.0)))) - 1
            ])

            ax1.set_xlabel(r'$B_p-R_p$ (mag)', fontsize=16)
            ax1.set_ylabel(r'$M_G$ (mag)', fontsize=16)

            ax2 = ax1.twiny()
            ax2.set_xlim(ax1.get_xlim())
            spttickvals = np.array([-0.037, 0.377, 0.782, 0.980, 1.84, 2.50, 3.36, 4.75])
            sptticklabs = np.array(['A0', 'F0', 'G0', 'K0', 'M0', 'M3', 'M5', 'M7'])
            xx = np.where((spttickvals >= math.floor(min(r['bp_rp'][zz]))) & (spttickvals <= math.ceil(max(r['bp_rp'][zz]))))[0]
            ax2.set_xticks(spttickvals[xx])
            ax2.set_xticklabels(sptticklabs[xx])
            ax2.set_xlabel('SpT', fontsize=16, labelpad=15)

            ax1.plot(chai[:, 1], chai[:, 0], zorder=1, label='Cha-I (0-5 Myr)')
            ax1.plot(usco[:, 1], usco[:, 0], zorder=2, label='USco (11 Myr)')
            ax1.plot(tuchor[:, 1], tuchor[:, 0], zorder=3, label='Tuc-Hor (40 Myr)')
            ax1.plot(pleiades[:, 1], pleiades[:, 0], zorder=4, label='Pleiades (125 Myr)')
            ax1.plot(mamajek[:, 2], mamajek[:, 1], zorder=5, label='Mamajek MS')

            for idx in yy2:
                msize = (17 - 12.0*(sep3d[idx].value/searchradpc.value))**2
                mcolor = Gchi2[idx]
                medge = 'black'
                mzorder = 7
                mshape = 'o' if (r['ruwe'][idx] < 1.2) else 's'

                if rvcut is not None:
                    if (np.isnan(RV[idx]) == False) and (np.abs(RV[idx]-Gvrpmllpmbb[idx, 0]) > rvcut) and (np.abs(RV[idx]-Gvrpmllpmbb[idx, 0])/RVerr[idx] > 2.0):
                        mshape = '+'
                        mcolor = 'black'
                        mzorder = 6
                    if (np.isnan(RV[idx]) == False) and (np.abs(RV[idx]-Gvrpmllpmbb[idx, 0]) <= rvcut):
                        medge = 'blue'

                sc = ax1.scatter([r['bp_rp'][idx]],
                                 [(r['phot_g_mean_mag'][idx] - (5.0*np.log10(gaiacoord.distance[idx].value)-5.0))],
                                 s=msize, c=('black' if mcolor == 'black' else mcolor),
                                 marker=mshape, edgecolors=medge, zorder=mzorder,
                                 vmin=0.0, vmax=vlim.value, cmap='cubehelix', label='_nolabel')
                if mcolor == 'black':
                    ddd = sc
                else:
                    ccc = sc

            ax1.scatter([], [], c='white', edgecolors='black', marker='o', s=12**2, label='RUWE < 1.2')
            ax1.scatter([], [], c='white', edgecolors='black', marker='s', s=12**2, label='RUWE >= 1.2')
            ax1.scatter([], [], c='white', edgecolors='blue', marker='o', s=12**2, label='RV Comoving')
            ax1.scatter([], [], c='black', marker='+', s=12**2, label='RV Outlier')

            ax1.plot(r['bp_rp'][yy[0]],
                     (r['phot_g_mean_mag'][yy[0]] - (5.0*np.log10(gaiacoord.distance[yy[0]].value)-5.0)),
                     'rx', markersize=18, mew=3, markeredgecolor='red', zorder=10, label=targname)

            ax1.legend(fontsize=11)
            if ccc is not None:
                cb = plt.colorbar(ccc, ax=ax1)
                cb.set_label(label='Velocity Difference (km/s)', fontsize=14)

            _save_or_skip(fig, figname)

    except Exception as e:
        print(f"DEBUG: CMD plot failed ({type(e).__name__}: {e}); continuing.")

    # ---------- PM plot (THIS is where your max(empty) was happening) ----------
    try:
        zz2 = np.where((sep3d.value < searchradpc.value) & (Gchi2 < vlim.value) &
                       (sep.degree > 1e-5) & (Cangle.degree > convergcut))[0]
        yy2 = zz2[np.argsort((-Gchi2)[zz2])] if zz2.size > 0 else np.array([], dtype=int)
        zz3 = np.where((sep3d.value < searchradpc.value) & (sep.degree > 1e-5))[0]

        if yy2.size == 0:
            print("DEBUG: PM plot selection empty; skipping PM plot.")
        else:
            figname = outdir + targname.replace(" ", "") + "pmd.png"
            fig, ax1 = plt.subplots(figsize=(12, 8))
            ccc = None
            ddd = None

            pmra_sel = np.array(r['pmra'][zz2])
            pmdec_sel = np.array(r['pmdec'][zz2])

            ax1.axis([
                (pmra_sel.max() + 0.05*np.ptp(pmra_sel)),
                (pmra_sel.min() - 0.05*np.ptp(pmra_sel)),
                (pmdec_sel.min() - 0.05*np.ptp(pmra_sel)),
                (pmdec_sel.max() + 0.05*np.ptp(pmra_sel))
            ])

            ax1.errorbar(r['pmra'][yy2], r['pmdec'][yy2],
                         yerr=r['pmdec_error'][yy2], xerr=r['pmra_error'][yy2],
                         fmt='none', ecolor='k')

            ax1.scatter([r['pmra'][zz3]], [r['pmdec'][zz3]],
                        s=(0.5)**2, marker='o', c='black', zorder=2, label='Field')

            for idx in yy2:
                msize = (17 - 12.0*(sep3d[idx].value/searchradpc.value))**2
                mcolor = Gchi2[idx]
                medge = 'black'
                mzorder = 7
                mshape = 'o' if (r['ruwe'][idx] < 1.2) else 's'

                if rvcut is not None:
                    if (np.isnan(RV[idx]) == False) and (np.abs(RV[idx]-Gvrpmllpmbb[idx, 0]) > rvcut) and (np.abs(RV[idx]-Gvrpmllpmbb[idx, 0])/RVerr[idx] > 2.0):
                        mshape = '+'
                        mcolor = 'black'
                        mzorder = 6
                    if (np.isnan(RV[idx]) == False) and (np.abs(RV[idx]-Gvrpmllpmbb[idx, 0]) <= rvcut):
                        medge = 'blue'

                sc = ax1.scatter([r['pmra'][idx]], [r['pmdec'][idx]],
                                 s=msize, c=('black' if mcolor == 'black' else mcolor),
                                 marker=mshape, edgecolors=medge, zorder=mzorder,
                                 vmin=0.0, vmax=vlim.value, cmap='cubehelix', label='_nolabel')
                if mcolor == 'black':
                    ddd = sc
                else:
                    ccc = sc

            ax1.scatter([], [], c='white', edgecolors='black', marker='o', s=12**2, label='RUWE < 1.2')
            ax1.scatter([], [], c='white', edgecolors='black', marker='s', s=12**2, label='RUWE >= 1.2')
            ax1.scatter([], [], c='white', edgecolors='blue', marker='o', s=12**2, label='RV Comoving')
            ax1.scatter([], [], c='black', marker='+', s=12**2, label='RV Outlier')

            ax1.plot(Pgaia['pmra'][minpos], Pgaia['pmdec'][minpos],
                     'rx', markersize=18, mew=3, markeredgecolor='red', zorder=3, label=targname)

            ax1.set_xlabel(r'$\mu_{RA}$ (mas/yr)', fontsize=22, labelpad=10)
            ax1.set_ylabel(r'$\mu_{DEC}$ (mas/yr)', fontsize=22, labelpad=10)
            ax1.legend(fontsize=12)

            if ccc is not None:
                cb = plt.colorbar(ccc, ax=ax1)
                cb.set_label(label='Tangential Velocity Difference (km/s)', fontsize=18, labelpad=10)

            _save_or_skip(fig, figname)

    except Exception as e:
        print(f"DEBUG: PM plot failed ({type(e).__name__}: {e}); continuing.")

    # ---------- (Optional) You can keep your remaining plots/GALEX/WISE/ROSAT code as-is ----------
    # The key change for batch stability is: NEVER early-return on empty plot selections.
    # We now always proceed to output tables.

# ---------- Rotation Period (Prot) vs Color (Bp-Rp) Plot ----------
    try:
        # Selection: radial distance, velocity limits, and convergence cuts
        zz2 = np.where((sep3d.value < searchradpc.value) & (Gchi2 < vlim.value) &
                       (sep.degree > 1e-5) & (Cangle.degree > convergcut))[0]
        
        # Sort by Gchi2 for plotting order (best candidates on top)
        yy2 = zz2[np.argsort((-Gchi2)[zz2])] if zz2.size > 0 else np.array([], dtype=int)

        if yy2.size == 0:
            print("DEBUG: Prot vs Bp-Rp plot selection empty; skipping.")
        else:
            figname = outdir + targname.replace(" ", "") + "_rot_color.png"
            fig, ax1 = plt.subplots(figsize=(12, 8))
            
            # Extract data - Ensure 'prot' exists in your dictionary/table 'r'
            # If your rotation column name is different, update 'prot' here
            prot_all = np.array(r['prot'])
            bprp_all = np.array(r['Bp-Rp'])
            
            # 1. Plot the 'Field' or background stars in the background
            # Only plot stars that have an actual rotation period measurement
            valid_prot = np.where(~np.isnan(prot_all))[0]
            ax1.scatter(bprp_all[valid_prot], prot_all[valid_prot], 
                        s=5, marker='.', c='gray', alpha=0.3, label='Field Stars')

            # 2. Loop through selected candidates (yy2) to plot with specific symbology
            ccc = None
            for idx in yy2:
                if np.isnan(prot_all[idx]): 
                    continue
                
                # Dynamic sizing based on 3D distance
                msize = (17 - 12.0 * (sep3d[idx].value / searchradpc.value))**2
                mcolor = Gchi2[idx]
                medge = 'black'
                mzorder = 7
                
                # Shape based on RUWE (standard for Gaia binary/quality flag)
                mshape = 'o' if (r['ruwe'][idx] < 1.2) else 's'

                # Blue edge for stars that are RV comoving
                if rvcut is not None:
                    if (not np.isnan(RV[idx])) and (np.abs(RV[idx] - Gvrpmllpmbb[idx, 0]) <= rvcut):
                        medge = 'blue'
                
                sc = ax1.scatter(bprp_all[idx], prot_all[idx],
                                 s=msize, c=mcolor, marker=mshape, 
                                 edgecolors=medge, zorder=mzorder,
                                 vmin=0.0, vmax=vlim.value, cmap='cubehelix_r')
                ccc = sc

            # 3. Add the Target/Center star for reference (if it has a prot)
            # You might need to adjust where you get the target's Bp-Rp and Prot
            # ax1.plot(target_bprp, target_prot, 'rx', markersize=18, mew=3, label=targname)

            # Formatting
            ax1.set_xlabel(r'$G_{BP} - G_{RP}$ (mag)', fontsize=20)
            ax1.set_ylabel(r'Rotation Period (days)', fontsize=20)
            ax1.set_yscale('log')  # Rotation plots are often clearer on a log scale
            
            # Custom Legend
            ax1.scatter([], [], c='white', edgecolors='black', marker='o', s=100, label='RUWE < 1.2')
            ax1.scatter([], [], c='white', edgecolors='black', marker='s', s=100, label='RUWE $\geq$ 1.2')
            ax1.scatter([], [], c='white', edgecolors='blue', marker='o', s=100, label='RV Comoving')
            ax1.legend(loc='upper right', fontsize=12)

            if ccc is not None:
                cb = plt.colorbar(ccc, ax=ax1)
                cb.set_label('$\Delta V_{tan}$ (km/s)', fontsize=16)

            ax1.grid(True, which="both", ls="-", alpha=0.2)
            _save_or_skip(fig, figname)

    except Exception as e:
        print(f"DEBUG: Prot vs Bp-Rp plot failed ({type(e).__name__}: {e}); continuing.")
    # ---------- Output tables ----------
    print('Creating Output Tables with Results')

    zz = np.where((sep3d.value < searchradpc.value) & (Gchi2 < vlim.value))[0]
    sortlist = np.argsort(sep3d[zz]) if zz.size > 0 else np.array([], dtype=int)
    yy = zz[sortlist] if zz.size > 0 else np.array([], dtype=int)

    fmt1 = "%28s %11.7f %11.7f %6.3f %6.3f %11.3f %8.4f %8.4f %8.2f %8.2f %8.2f %8.3f %4s %8.6f %6.2f %7.3f %7.3f %35s %11.3f %11.3f %11.3f %11.3f %11.3f %11.3f"
    fmt2 = fmt1
    filename = outdir + targname.replace(" ", "") + ".txt"

    warnings.filterwarnings("ignore", category=UserWarning)
    header = ("GaiaDR3                               RA         DEC   Gmag  Bp-Rp  Voff(km/s) Sep(deg)   3D(pc) "
              "Vr(pred)  Vr(obs)    Vrerr Plx(mas)  SpT    FnuvJ  W1-W3    RUWE  XCrate                               "
              "RVsrc    PMRApred   PMDecpred        PMRA     PMRAerr       PMDec    PMDecerr\n")
    with open(filename, 'w') as f:
        f.write(header)

    for idx in yy:
        with open(filename, 'a') as f:
            f.write(fmt2 % (
                r['designation'][idx],
                gaiacoord.ra[idx].value, gaiacoord.dec[idx].value,
                r['phot_g_mean_mag'][idx], r['bp_rp'][idx],
                Gchi2[idx], sep[idx].value, sep3d[idx].value,
                Gvrpmllpmbb[idx, 0], RV[idx], RVerr[idx],
                r['parallax'][idx],
                sptstring[idx],
                fnuvj[idx],
                W13[idx],
                r['ruwe'][idx],
                ROSATflux[idx],
                RVsrc[idx],
                Gpmrapmdec[idx, 0], Gpmrapmdec[idx, 1],
                gaiacoord.pm_ra_cosdec.value[idx], r['pmra_error'][idx],
                gaiacoord.pm_dec.value[idx], r['pmdec_error'][idx]
            ))
            f.write("\n")

    # convert to CSV the same way you already do
    csv_filename = outdir + targname.replace(" ", "") + ".csv"
    original_headers = pd.read_csv(filename, sep=r'\s+', nrows=0).columns.tolist()
    new_names = ['Catalog', 'Type'] + original_headers
    csv_file = pd.read_csv(filename, sep=r'\s+', names=new_names, skiprows=1, index_col=False)
    csv_file.to_csv(csv_filename, index=False)

    if verbose:
        print('All output can be found in ' + outdir)

    return outdir
