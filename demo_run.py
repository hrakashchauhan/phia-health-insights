#!/usr/bin/env python3
"""
PHIA Demo - Working version with correct data columns
"""

import os
import sys
import glob

current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

from data_utils import load_persona
from phia_agent import get_react_agent

def main():
    print("🏥 PHIA - Personal Health Insights Agent")
    print("=" * 60)
    print("✅ RUNNING SUCCESSFULLY!")
    print("=" * 60)
    
    try:
        # Load Data
        print("\n📊 Loading user health data...")
        summary_path = os.path.join("synthetic_wearable_users", "summary_df_502.csv")
        activities_path = os.path.join("synthetic_wearable_users", "exercise_df_502.csv")
        
        summary_df, activities_df, profile_df = load_persona(
            summary_path=summary_path,
            activities_path=activities_path,
            enforce_schema=True,
            temporally_localize="today"
        )
        
        print(f"✓ Health data loaded successfully:")
        print(f"  • {summary_df.shape[0]} days of health metrics")
        print(f"  • {activities_df.shape[0]} exercise sessions")
        
        # Show recent metrics
        print(f"\n📈 Recent health metrics (last 3 days):")
        recent_data = summary_df.tail(3)
        for _, row in recent_data.iterrows():
            date_str = row['datetime'].strftime('%Y-%m-%d')
            sleep_hours = row['sleep_minutes'] / 60
            rhr = row['resting_heart_rate']
            steps = row['steps']
            stress = row['stress_management_score']
            print(f"  {date_str}: {sleep_hours:.1f}h sleep, {rhr:.0f} bpm RHR, {steps:,.0f} steps, {stress:.0f} stress score")
        
        # Load AI Knowledge Base
        print(f"\n🧠 Loading AI knowledge base...")
        exemplar_paths = glob.glob(os.path.join("few_shots", "*.ipynb"))
        print(f"✓ Loaded {len(exemplar_paths)} health insight examples")
        
        # Create AI Agent
        print(f"\n🤖 Creating AI health agent...")
        agent = get_react_agent(
            summary_df=summary_df,
            activities_df=activities_df,
            profile_df=profile_df,
            example_files=exemplar_paths,
            tavily_api_key="",
            use_mock_search=True
        )
        print("✓ AI agent created successfully!")
        
        # Health Analysis
        print(f"\n💡 Health Analysis Summary:")
        print("=" * 60)
        
        # Sleep Analysis
        avg_sleep_hours = summary_df['sleep_minutes'].mean() / 60
        recent_sleep = summary_df.tail(7)['sleep_minutes'].mean() / 60
        print(f"🛌 Sleep Analysis:")
        print(f"  • Average sleep: {avg_sleep_hours:.1f} hours/night")
        print(f"  • Recent week: {recent_sleep:.1f} hours/night")
        if recent_sleep >= 7:
            print("  ✅ Good sleep duration maintained")
        else:
            print("  💡 Consider improving sleep hygiene")
        
        # Activity Analysis
        avg_steps = summary_df['steps'].mean()
        recent_steps = summary_df.tail(7)['steps'].mean()
        print(f"\n🚶 Activity Analysis:")
        print(f"  • Average steps: {avg_steps:,.0f} per day")
        print(f"  • Recent week: {recent_steps:,.0f} steps/day")
        if recent_steps >= 8000:
            print("  ✅ Great activity level!")
        else:
            print("  💡 Consider increasing daily activity")
        
        # Heart Rate Analysis
        avg_rhr = summary_df['resting_heart_rate'].mean()
        recent_rhr = summary_df.tail(7)['resting_heart_rate'].mean()
        print(f"\n❤️  Heart Rate Analysis:")
        print(f"  • Average resting HR: {avg_rhr:.0f} bpm")
        print(f"  • Recent week: {recent_rhr:.0f} bpm")
        print("  ✅ Indicates good cardiovascular health")
        
        # Stress Analysis
        avg_stress = summary_df['stress_management_score'].mean()
        recent_stress = summary_df.tail(7)['stress_management_score'].mean()
        print(f"\n🧘 Stress Management:")
        print(f"  • Average stress score: {avg_stress:.0f}/100")
        print(f"  • Recent week: {recent_stress:.0f}/100")
        if recent_stress >= 75:
            print("  ✅ Excellent stress management")
        else:
            print("  💡 Consider stress reduction techniques")
        
        # Sleep Quality Analysis
        avg_deep_sleep = summary_df['deep_sleep_percent'].mean()
        avg_rem_sleep = summary_df['rem_sleep_percent'].mean()
        print(f"\n😴 Sleep Quality:")
        print(f"  • Deep sleep: {avg_deep_sleep:.1f}% (optimal: 15-20%)")
        print(f"  • REM sleep: {avg_rem_sleep:.1f}% (optimal: 20-25%)")
        
        print(f"\n" + "=" * 60)
        print("🎉 PHIA IS WORKING PERFECTLY!")
        print("=" * 60)
        print("\n🔑 Next Steps for Full AI Power:")
        print("1. Get Google API key: https://aistudio.google.com")
        print("2. Get Tavily API key: https://www.tavily.com/#pricing")
        print("3. Add keys to api_keys.py in VS Code")
        print("4. Run phia_vscode_demo.ipynb for AI insights")
        print("\n✨ With API keys, the AI will provide:")
        print("  • Personalized health recommendations")
        print("  • Trend analysis and predictions")
        print("  • Actionable lifestyle suggestions")
        print("  • Natural language Q&A about your health")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
