import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import math

class chart_themes:
    white = {
        # Set font
        'font.family':  'sans-serif',
        'font.sans-serif' : 'Gotham',

        'legend.facecolor' : 'white',
        
    }
    dark = {
        'font.family':  'sans-serif',
        'font.sans-serif' : 'Gotham',

        # background:
        'figure.facecolor': '#2f3033',
        'axes.facecolor': '#202124',
        'savefig.facecolor': '#2f3033',
        # Axis Lines
        'axes.linewidth' : '0',
        # Font
        'text.color' : '0.9',
        'axes.labelcolor': '0.9',
        'font.family' : 'sans-serif',
        'xtick.color' : '0.9',
        'ytick.color' : '0.9',
        # Legend
        'legend.frameon' : 'True',
        'legend.facecolor' : '#2f3033',
        'legend.fancybox' : 'True',
        
    }
        
    blue = {
        'font.family':  'sans-serif',
        'font.sans-serif' : 'Gotham',

        # background: bluish dark grey
        'figure.facecolor': '#28345c',
        'axes.facecolor': '212946',
        'savefig.facecolor': '#28345c',
        # Axis Lines
        'axes.linewidth' : '0',
        # Font
        'text.color' : '0.9',
        'axes.labelcolor': '0.9',
        'font.family' : 'sans-serif',
        'xtick.color' : '0.9',
        'ytick.color' : '0.9',
        # Legend
        'legend.frameon' : 'True',
        'legend.facecolor' : '#28345c',
        'legend.fancybox' : 'True',
    }

def fix_array(func):
    def validate(*args):
        if args[0] is not None:
            if type(args[0]) != 'pandas.core.series.Series':
                    return func(pd.Series(args[0]))
            else:
                return func(args[0])
        else:
            print("Please, you need to input values to generate the stats!!")

    return validate

@fix_array
def get_data_info(x = None, top_results = 3):
    x_wihtout_miss = sum(x.notna())
    data_info = {'n' : x.shape[0],
    'missings' : x.isna().sum(),
    '%_missings' : x.isna().sum()/x.shape[0],
    'n_distinct' : x.drop_duplicates().shape[0],
    '%_distinct' : round(x.drop_duplicates().shape[0] / x.shape[0],2),
    'preview' : x.head(3).to_list(),
    }

    # if data are string (object)
    if x.dtype == 'O':
        data_info['type'] = "Characteres"
        if data_info['%_distinct'] <= 0.7:
            data_info['top_3'] = x.value_counts(ascending=False).head(top_results).to_dict()
            data_info['%_top_3'] = x.value_counts(ascending=False,normalize=True).head(top_results).to_dict()

    elif x.dtype == 'bool':
        data_info['type'] = "Boolean"
        data_info['n_True'] = x.sum()
        data_info['%_True'] = data_info['n_True'] / x_wihtout_miss
        data_info['n_False'] = x_wihtout_miss - data_info['n_True']
        data_info['%_False'] = data_info['n_False'] / x_wihtout_miss

    else:
        data_info['type'] = "Numeric"
        data_info['zeros'] = sum(x == 0)
        data_info['%_zeros'] = data_info['zeros'] / x_wihtout_miss
        data_info['positives'] = sum(x > 0)
        data_info['%_positives'] = data_info['positives'] / x_wihtout_miss
        data_info['negatives'] = sum(x < 0)
        data_info['%_negatives'] = data_info['negatives'] / x_wihtout_miss

    return data_info

@fix_array
def get_statistics(x):
    x = x.dropna()
    return({'n' : sum(x.notna()), 
    'mean' : x.mean(), 
    'std' : x.std(),
    'min' : x.min(),
    '1st quartile' : x.quantile(.25),
    'median' : x.median(),
    '3rd quartile' : x.quantile(.75),
    'max' : x.max(),
    'sum' : x.sum(), 
    'mode' : stats.mode(x)[0][0],
    'mode times' : stats.mode(x)[1][0],
    'cv' : stats.variation(x),
    'IQR' : stats.iqr(x)}
    )

@fix_array
def _removena(x):
    return list(x.dropna())

def plot_stats_univariate(x, title = None, MAIN_COLOR = 'aqua', theme = 'dark', glow = False):
    # Set Theme
    sns.set(style='dark')
    if theme == 'dark':
        plt.rcParams.update(chart_themes.dark)
    elif theme == 'blue':
        plt.rcParams.update(chart_themes.blue)
    else:
        plt.rcParams.update(chart_themes.white)

    # Get data Information about (zeros, missings)
    data_info = get_data_info(x)
    # Getting statistics
    stats = get_statistics(x)
    
    # Drop NA to build charts
    x = _removena(x)

    fig, axes = plt.subplots(5, sharex=True, figsize=(10, 6), gridspec_kw= {"height_ratios": (.3, 1, .3, .4, .5)})

    for ax in axes:
        if ax == axes[0]:
            # Set Chart's Title
            text = r'Univariate Descriptive Statistics - $\bf{}$'.format(title) if title is not None else "Univariate Descriptive Statistics"
            ax.set_title(text, loc = 'left', fontsize = 16)

            ax.set_yticklabels(['','Data'], rotation = 90, va = "top")

            ax.text(.01,.5,'Total Obs.: {}\nDistinct: {} ({}%)'.format(
                data_info['n'], 
                data_info['n_distinct'],
                    round(data_info['%_distinct'] * 100,1)),ha = 'left', transform=ax.transAxes, va = 'center')

            ax.text(.4,.5,'Missings: {} {}\nZeros: {} {}'.format(
                '--' if data_info['missings'] == 0 else data_info['missings'], 
                '' if data_info['missings'] == 0 else '(' + str(round(data_info['%_missings']*100,1)) + '%)',
                '--' if data_info['zeros'] == 0 else data_info['zeros'],
                '' if data_info['zeros'] == 0 else '(' + str(round(data_info['%_zeros']*100,1)) + '%)'), 
                ha = 'left', transform=ax.transAxes, va = 'center')

            ax.text(.7,.5,'Positives: {} {}\nNegatives: {} {}'.format(
                '--' if data_info['positives'] == 0 else data_info['positives'], 
                '' if data_info['positives'] == 0 else '(' + str(round(data_info['%_positives']*100,1)) + '%)',
                '--' if data_info['negatives'] == 0 else data_info['negatives'],
                '' if data_info['negatives'] == 0 else '(' + str(round(data_info['%_negatives']*100,1)) + '%)'),
                ha = 'left', transform=ax.transAxes, va = 'center')

            ax.set(xticklabels=[])

        elif ax == axes[1]:
            if glow:
                n_lines = 10
                diff_linewidth = 1.05
                alpha_value = 0.03
                for n in range(1, n_lines + 1):
                    sns.kdeplot(x, shade=False, color=MAIN_COLOR, ax=ax, common_grid=None, linewidth=2+(diff_linewidth*n), alpha=alpha_value)

            sns.kdeplot(x, shade=False, color=MAIN_COLOR, ax=ax, common_grid=None)

            kdeline = ax.lines[0]
            xs = kdeline.get_xdata()
            ys = kdeline.get_ydata()

            ax.vlines(stats['mean'], 0, np.interp(stats['mean'], xs, ys), color=MAIN_COLOR, ls=':', label = 'Average')
            ax.vlines(stats['median'], 0, np.interp(stats['median'], xs, ys), color='#00FF00', ls='-', label = 'Median')
            ax.vlines(stats['mode'], 0, np.interp(stats['mode'], xs, ys), color=MAIN_COLOR, ls='--', label = 'Mode')

            # Start first quartile
            ax.text(stats['1st quartile'], 0, round(stats['1st quartile'],1), ha = 'center', va = 'top', color = MAIN_COLOR, weight='bold', size = 9)
            ax.text(stats['3rd quartile'], 0, round(stats['3rd quartile'],1), ha = 'center', va = 'top', color = MAIN_COLOR, weight='bold', size = 9)

            ax.fill_between(xs, 0, ys, facecolor=MAIN_COLOR, alpha=0.2)
            limits = np.where([(stats['1st quartile'] <= xs) & (xs <= stats['3rd quartile'])])[1]
            ax.fill_between(xs[limits], 0, ys[limits], interpolate=True, facecolor=MAIN_COLOR, alpha=0.2)

            ax.legend()

        elif ax == axes[2]:
            sns.histplot(x, color = MAIN_COLOR, ax = ax)

        elif ax == axes[3]:
            sns.boxplot(x = x,  color = MAIN_COLOR, ax = ax)

            for n_print in range(int(stats['min']), int(stats['max']), math.ceil(max(stats['max'], abs(stats['min'])) / 8)):
                ax.text(x = n_print, y = 0.5, s = n_print , ha = 'center', va = 'top', color = MAIN_COLOR, alpha = .2, size = 12)

        elif ax == axes[4]:
            ax.set_yticklabels(['','Statistics'], rotation = 90, va = "center")
            
            ax.text(.01,.5,'Sum Total: {}\nMax: {}\nMin: {}'.format(
                round(stats['sum'], 2),
                round(stats['max'], 2),
                round(stats['min'], 2)), ha = 'left', transform=ax.transAxes, va = 'center')
            
            ax.text(.4,.5,'1st Quartile: {}\n3rd Quartile: {}\nIQR: {}\nCV: {}'.format(
                round(stats['1st quartile'],2), 
                round(stats['3rd quartile'],2),
                round(stats['IQR'],2),
                round(stats['cv'],2)), ha = 'left', transform=ax.transAxes, va = 'center')

            ax.text(.7, .5, 'Mode: {} ({} Times)\nMedian: {}\nAverage: {}\nStd.: {}'.format(
                round(stats['mode'],2),
                stats['mode times'],
                round(stats['median'], 2),
                round(stats['mean'], 2),
                round(stats['std'], 2)), ha = 'left', transform=ax.transAxes, va = 'center')

    plt.show()
    return fig, ax

def count_category(x, auto_group = True):
    x = [str(i) for i in x]

    count = pd.Series(x).value_counts(ascending=False).to_dict()
    n_categories = len(count)

    list_others = []
    if auto_group:
        i = 0
        total_others = 0
        new_count = {}
        if n_categories > 15:
            for index, value in count.items():
                if i > 9:
                    total_others += value
                    list_others += [index]
                else:
                    new_count[index] = value
                i += 1
            # Set new Variables
            new_count['Others'] = total_others
            count = new_count
            n_categories = len(count)
    
    df = pd.DataFrame(count.items(), columns=['keys', 'n'])
    df['percent'] = df['n'] / df['n'].sum()
    df['percentUp'] = df['percent'][::-1].cumsum()[::-1]
    df['percentDown'] = df['percent'].cumsum()

    return df.to_dict('list'), list_others


def plot_cat_distribution(x, title = None, BAR_COLOR = 'lime', theme = 'dark', auto_group = True):
    # Set Theme
    sns.set(style='dark')
    if theme == 'dark':
        plt.rcParams.update(chart_themes.dark)
    elif theme == 'blue':
        plt.rcParams.update(chart_themes.blue)
    else:
        plt.rcParams.update(chart_themes.white)

    n_miss = pd.isna(x).sum()
    n_total = len(x)
    x = _removena(x)

    count, list_others = count_category(x, auto_group)
    n_categories = len(count['keys'])

    if (auto_group) & ('Others' in count['keys']):
        total_others = count['n'][n_categories-1]
    else:
        total_others = 0

    fig, ax = plt.subplots(figsize=(10, n_categories * .7))
    size_obs = 11 - n_categories * 0.05
    size_perc = 9 - n_categories * 0.05

    values = count['n']
    total = sum(values)
    categories = count['keys']
    # Get the most important values
    top = np.quantile(values, .7)

    sns.barplot(x = values, y = categories, ax = ax, alpha = 0.3, color="gray")

    for index, bar in enumerate(ax.patches):
        value = bar.get_width()

        if value > np.max(values) / 2:
            ax.text(x= value,y = index, s = '{:.0f} ({:.1f}%)  '.format(value, value / total * 100), va = 'bottom', ha = 'right', weight='bold', fontsize = size_obs)

            ax.text(x = value, y = index + .1, s = 'Down: {:.1f}% | Up: {:.1f}%  '.format(
                sum(values[:index + 1]) / total * 100,
                sum(values[index:]) / total * 100), va = 'top', ha = 'right', fontsize = size_perc, style = 'italic')
        else:
            ax.text(x= value,y = index, s = '  {:.0f} ({:.1f}%)'.format(value, value / total * 100), va = 'bottom', ha = 'left', weight='bold', fontsize = size_obs)
            ax.text(x = value, y = index + .1, s = '  Down: {:.1f}% | Up: {:.1f}%  '.format(
                sum(values[:index + 1]) / total * 100,
                sum(values[index:]) / total * 100), va = 'top', ha = 'left', fontsize = size_perc, style = 'italic')

        if total_others == value:
            bar.set_color('red')
        elif value > top:
            bar.set_color(BAR_COLOR)

    ax.text(x = 0, y = 1, s = 'Below the number of occurrences, the cumulative sum of the percentages.', ha = 'left', transform=ax.transAxes, va = 'bottom', fontsize = 8)

    title = r'Distribution of $\bf{}$'.format(title) if title is not None else 'Distribution of Categorical Variable'
    
    ax.set_title(title, loc = 'left', va = 'bottom', fontsize = 16)
    ax.set(xticklabels=[])

    ax.set_xlabel(r'Total of records analyzed $\bf{}$'.format(total) + ' | ' + 
        r'$\bf{}$ Missing Values'.format("No" if n_miss == 0 else str(n_miss) + '('+ round(n_miss/n_total*100,1) +'%)'), loc = 'left', fontsize = 12, va = 'center')

    # Annotation below the chart
    if list_others != []:
        text = r'$\bfOthers$ contain $\bf{}$ categories: '.format(len(list_others))
        text = text + '|'.join(list_others)
        for i in range(95, len(text), 95):
            while text[i] != '|': 
                i += 1
            text = text[:i] + '\n' + text[i+1:]

        #plt.figtext(plt.axis()[0], 0.01, text, fontsize=9)
        plt.annotate(text, (0,0), (0, -30), xycoords='axes fraction', textcoords='offset points', va='center', fontsize = 9)
    plt.show()

    return fig, ax

def plot_stats_bivariate(X, y, MAIN_COLOR = 'royalblue', theme = 'dark',x_name = None, y_name = None):
    # Set Theme
    sns.set(style='dark')
    if theme == 'dark':
        plt.rcParams.update(chart_themes.dark)
    elif theme == 'blue':
        plt.rcParams.update(chart_themes.blue)
    else:
        plt.rcParams.update(chart_themes.white)
        
    slope, intercept, r_value, p_value, slope_std_error = stats.linregress(X,y)
    y_pred = intercept + X * slope
    mae = np.mean(abs(y-y_pred))
    mse = np.mean(abs(y-y_pred)**2)
    rmse = math.sqrt(mse)
    mape = np.mean(abs((y - y_pred) / y)) * 100

    fig, ax = plt.subplots(figsize = (14,6), ncols=2)
    sns.regplot(x=X, y=y, fit_reg=True, ci = False,scatter_kws = {'color': MAIN_COLOR, 'alpha' : .3}, line_kws = {'color' : MAIN_COLOR}, ax = ax[0])
    # ax[0].annotate(f'Slope: {slope:.3f}\nIntercept: {intercept:.2f}\nR2: {r_value:.3f}\np: {p_value:.3f}', xy=(0.05, 0.9), xycoords='axes fraction',
    #                     ha='left', va='center', bbox={'boxstyle': 'round', 'fc': 'powderblue', 'ec': 'navy'}, fontsize = 8)
    sns.residplot(x=X, y=y, scatter_kws = {'color': MAIN_COLOR, 'alpha' : .3}, line_kws={'color': 'red', 'lw': 2, 'alpha': 0.7}, ax=ax[1]).axhline(0, color = 'red')
    title = 'Bivariate Analysis'
    if x_name is not None and y_name is not None:
        title = title + r' $\bf{}$ and $\bf{}$'.format(x_name, y_name)
    ax[0].text(x = 0, y = 1.15, s= title, va = 'top', fontsize = 16, transform= ax[0].transAxes)
    ax[0].text(x = 0, y = 1.05, s= 'Scatter with Linear Regression', va = 'top', fontsize = 11, transform= ax[0].transAxes)
    ax[1].text(x = 0, y = 1.05, s= 'Residual Chart', va = 'top', fontsize = 11, transform= ax[1].transAxes)

    ax[0].text(x = 0, y = -0.2, s= f'Intercept: {intercept:.3f}', va = 'top', fontsize = 11, transform= ax[0].transAxes)
    ax[0].text(x = 0, y = -0.25, s= f'Slope: {slope:.3f}', va = 'top', fontsize = 11, transform= ax[0].transAxes)
    ax[0].text(x = 0, y = -0.3, s= f'R2: {r_value:.3f}', va = 'top', fontsize = 11, transform= ax[0].transAxes)
    ax[0].text(x = 0, y = -0.35, s= f'P Value: {p_value:.3f}', va = 'top', fontsize = 11, transform= ax[0].transAxes)

    ax[1].text(x = 0, y = -0.2, s= f'Mean Absolute Error (MAE): {mae:.3f}', va = 'top', fontsize = 11, transform= ax[1].transAxes)
    ax[1].text(x = 0, y = -0.25, s= f'Mean Squared Error (MSE): {mse:.3f}', va = 'top', fontsize = 11, transform= ax[1].transAxes)
    ax[1].text(x = 0, y = -0.3, s= f'Root Mean Squared Error (RMSE): {rmse:.3f}', va = 'top', fontsize = 11, transform= ax[1].transAxes)
    ax[1].text(x = 0, y = -0.35, s= f'Mean Absolute Perc. Error (MAPE): {mape:.3f}', va = 'top', fontsize = 11, transform= ax[1].transAxes)

    sns.despine()
    plt.subplots_adjust(bottom=.3)
    plt.show()
    return fig, ax

def plot_cat_bivariate(X, y, MAIN_COLOR = 'royalblue', theme = 'dark', x_name = None, y_name = None):
    # Set Theme
    # sns.set(style='dark')
    sns.set_theme(style="ticks")
    if theme == 'dark':
        plt.rcParams.update(chart_themes.dark)
    elif theme == 'blue':
        plt.rcParams.update(chart_themes.blue)
    else:
        plt.rcParams.update(chart_themes.white)

    fig, ax = plt.subplots(figsize=(4,4), dpi= 100, facecolor='w', edgecolor='k')

    # Draw a nested boxplot to show bills by day and time
    sns.boxplot(x=X, y=y, color = MAIN_COLOR, boxprops=dict(alpha=.3), ax = ax).set(xlabel = x_name, ylabel = y_name)
    sns.despine(offset=10, trim=True)

    title = 'Bivariate Analysis'
    if x_name is not None and y_name is not None:
        title = title + r' $\bf{}$ and $\bf{}$'.format(x_name, y_name)

    ax.text(x=0.0, y=1.1, s= title, fontsize=16, ha='left', va='bottom', transform=ax.transAxes)

    plt.subplots_adjust(bottom=.3, left =.2)
    
    plt.show()
    return fig, ax
